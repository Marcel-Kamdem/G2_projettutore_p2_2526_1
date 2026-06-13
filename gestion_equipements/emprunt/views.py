from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Mouvement
from .mouvement_service import MouvementService
from .forms import MouvementForm, MouvementModificationForm, ImportMouvementForm


# ─── Import Excel ──────────────────────────────────────────────────────────────

def importer_mouvements_view(request):
    form = ImportMouvementForm()
    contexte = {'form': form}

    if request.method == 'POST':
        form = ImportMouvementForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier_excel']
            succes, erreurs = MouvementService.importer_depuis_excel(fichier)
            contexte['succes'] = succes
            contexte['erreurs'] = erreurs

    return render(request, 'emprunt/importer.html', contexte)


# ─── Liste mouvements (emprunts + sorties, hors entrées) ──────────────────────



def liste_mouvements(request):
    query = request.GET.get('q', '')
    type_filtre = request.GET.get('type', '')
    etat_filtre = request.GET.get('etat', '')

    mouvements = MouvementService.liste_mouvements(query, type_filtre, etat_filtre)
    # On exclut les planifiés de la liste principale (ils ont leur propre vue)
    # mouvements = mouvements.exclude(etat="PLANIFIE").order_by('-date_operation')
    mouvements = mouvements.order_by('-date_operation')

    stats = MouvementService.stats_mouvements()

    return render(request, "emprunt/liste.html", {
        "mouvements": mouvements,
        "stats": stats,
        "query": query,
        "type_filtre": type_filtre,
        "etat_filtre": etat_filtre,
        "types": Mouvement.TYPE_OPERATION_CHOICES,
        "etats": Mouvement.ETAT_CHOICES,
    })


# ─── Détail ────────────────────────────────────────────────────────────────────

def detail_mouvement(request, pk):
    mouvement = get_object_or_404(Mouvement, pk=pk)
    return render(request, 'emprunt/detail.html', {'mouvement': mouvement})


# ─── Créer ─────────────────────────────────────────────────────────────────────

@login_required
def creer_mouvement(request):
    if request.method == "POST":
        form = MouvementForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.gestionnaire = request.user

            # Vérification doublon emprunt actif
            if mouvement.type_operation == 'emprunt':
                existe = Mouvement.objects.filter(
                    equipement=mouvement.equipement,
                    type_operation='emprunt',
                    etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
                ).exists()
                if existe:
                    messages.error(request, "Cet équipement est déjà en cours d'emprunt.")
                    return render(request, 'emprunt/form.html', {'form': form, 'titre': 'Créer un mouvement', 'action': 'Créer'})

            mouvement.date_retour_effectif = None
            mouvement.save()

            if mouvement.etat == "PLANIFIE":
                return redirect('liste_planifications')
            return redirect('liste_mouvements')
    else:
        form = MouvementForm()

    return render(request, 'emprunt/form.html', {
        'form': form,
        'titre': 'Créer un mouvement',
        'action': 'Créer'
    })


# ─── Modifier ──────────────────────────────────────────────────────────────────

@login_required
def modifier_mouvement(request, pk):
    mouvement = get_object_or_404(Mouvement, pk=pk)
    form = MouvementModificationForm(request.POST or None, instance=mouvement)
    if form.is_valid():
        form.save()
        return redirect('liste_mouvements')
    return render(request, 'emprunt/form.html', {
        'form': form,
        'titre': 'Modifier le mouvement',
        'action': 'Modifier'
    })


# ─── Supprimer ─────────────────────────────────────────────────────────────────

def supprimer_mouvement(request, pk):
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.delete()
    return redirect('liste_mouvements')


# ─── Planifications ────────────────────────────────────────────────────────────

def liste_planifications(request):
    planifications = Mouvement.objects.filter(
        type_operation='emprunt',
        etat="PLANIFIE"
    ).order_by('-date_operation')
    return render(request, 'emprunt/planifications.html', {'planifications': planifications})


def valider_planification(request, pk):
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.etat = "VALIDE"
    mouvement.message_admin = "Votre emprunt a été validé par l'administrateur."
    mouvement.save()
    return redirect(request.META.get('HTTP_REFERER', 'liste_planifications'))


def refuser_planification(request, pk):
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.etat = "REFUSE"
    mouvement.message_admin = "Votre emprunt a été refusé par l'administrateur."
    mouvement.save()
    return redirect(request.META.get('HTTP_REFERER', 'liste_planifications'))


def passer_en_cours(request, pk):
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.etat = "EN_COURS"
    mouvement.save()
    return redirect('liste_planifications')