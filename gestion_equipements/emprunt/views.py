from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from emprunt.models import Emprunt
from emprunt.emprunt_service import EmpruntService
#from gestion_equipements import emprunt
from .forms import EmpruntForm, EmpruntModificationForm, ImportEmpruntForm
#
def valider_emprunt(request, pk):
    emprunt = Emprunt.objects.get(id=id)
    emprunt.etat = "VALIDE"
    emprunt.save()
    return redirect('loans')

def refuser_emprunt(request, id):
    emprunt = Emprunt.objects.get(id=id)
    emprunt.etat = "REFUSE"
    emprunt.save()
    return redirect('loans')



def importer_emprunts_view(request):
    form = ImportEmpruntForm()
    contexte = {'form': form}

    if request.method == 'POST':
        form = ImportEmpruntForm(request.POST, request.FILES)

        if form.is_valid():
            fichier = request.FILES['fichier_excel']
            succes, erreurs = EmpruntService.importer_depuis_excel(fichier)

            contexte['succes'] = succes
            contexte['erreurs'] = erreurs

    return render(request, 'emprunt/importer.html', contexte)


def liste_emprunts(request):
    query = request.GET.get('q', '')
    etat_filtre = request.GET.get('etat', '')

    emprunts = EmpruntService.liste_emprunts(query, etat_filtre)
    emprunts = emprunts.exclude(etat="PLANIFIE").order_by('-date_empr')

    stats = {
        "total": Emprunt.objects.count(),
        "en_cours": Emprunt.objects.filter(etat="EN_COURS").count(),
        "planifies": Emprunt.objects.filter(etat="PLANIFIE").count(),
        "valides": Emprunt.objects.filter(etat="VALIDE").count(),
        "retournes": Emprunt.objects.filter(etat="RETOURNE").count(),
        "expires": Emprunt.objects.filter(etat="EXPIRE").count(),
        "annules": Emprunt.objects.filter(etat="ANNULE").count(),
    }

    return render(request, "emprunt/liste.html", {
        "emprunts": emprunts,
        "stats": stats,
        "query": query,
        "etat_filtre": etat_filtre,
        "etats": Emprunt.EMPRUNT_STATE,
    })


def detail_emprunt(request, pk):
    emprunt = get_object_or_404(Emprunt, pk=pk)
    return render(request, 'emprunt/detail.html', {'emprunt': emprunt})


@login_required
def creer_emprunt(request):
    if request.method == "POST":
        form = EmpruntForm(request.POST)

        if form.is_valid():
            emprunt = form.save(commit=False)

            existe = Emprunt.objects.filter(
                equipement=emprunt.equipement,
                etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
            ).exists()

            if existe:
                messages.error(request, "Cet équipement est déjà utilisé")
                return render(request, 'emprunt/form.html', {'form': form})

            emprunt.gestionnaire = request.user
            emprunt.date_retour_effect = None
            emprunt.save()
            form.save_m2m()

            if emprunt.etat == "PLANIFIE":
                return redirect('liste_planifications')
            return redirect('liste_emprunts')

    else:
        form = EmpruntForm()

    return render(request, 'emprunt/form.html', {'form': form})


@login_required
def modifier_emprunt(request, pk):
    emprunt = get_object_or_404(Emprunt, pk=pk)
    #form = EmpruntForm(request.POST or None, instance=emprunt)
    form = EmpruntModificationForm(request.POST or None,instance=emprunt)
    if form.is_valid():
        form.save()
        
        #updated = form.save(commit=False)

        #existe = Emprunt.objects.filter(
         #   equipement=updated.equipement,
          #  etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
        #).exclude(pk=emprunt.pk).exists()

        #if existe:
        #    messages.error(request, "Cet équipement est déjà emprunté")
         #   return render(request, 'emprunt/form.html', {'form': form})

        #updated.save()
        #form.save_m2m()

        #if updated.etat == "PLANIFIE":
         #   return redirect('liste_planifications')
        return redirect('liste_emprunts')

    return render(request, 'emprunt/form.html', {'form': form})


def supprimer_emprunt(request, pk):
    emprunt = get_object_or_404(Emprunt, pk=pk)
    emprunt.delete()
    return redirect('liste_emprunts')




def liste_planifications(request):
    planifications = Emprunt.objects.filter(etat="PLANIFIE").order_by('-date_empr')
    return render(request, 'emprunt/planifications.html', {'planifications': planifications})


def valider_planification(request, pk):
    emprunt = Emprunt.objects.get(pk=pk)
    emprunt.etat = "VALIDE"
    emprunt.message_admin = "Votre emprunt a été validé par l'administrateur."
    #plan = get_object_or_404(Emprunt, pk=pk)
    #plan.etat = "VALIDE"
    #plan.save()
    emprunt.save()
    return redirect(request.META.get('HTTP_REFERER'))


def refuser_planification(request, pk):
    emprunt = Emprunt.objects.get(pk=pk)
    emprunt.etat = "REFUSE"
    emprunt.message_admin = "Votre emprunt a été refusé par l'administrateur."
    emprunt.save()
    #plan = get_object_or_404(Emprunt, pk=pk)
    #plan.etat = "REFUSE"
    #plan.save()
    #return redirect('liste_planifications')
    return redirect(request.META.get('HTTP_REFERER'))


def passer_en_cours(request, pk):
    plan = get_object_or_404(Emprunt, pk=pk)
    plan.etat = "EN_COURS"
    plan.save()
    return redirect('liste_planifications')