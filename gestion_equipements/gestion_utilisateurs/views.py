from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .forms import LoginForm, GestionnaireCreationForm, ModifierMotDePasseForm
from .models import Administrateur, Gestionnaire
from emprunt.models import Mouvement
from inventaire.models import Inventaire


def index(request):
    return render(request, "gestion_utilisateurs/index.html")


def login_view(request):
    error = False
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect('dashboard_admin')
                return redirect('dashboard_gestionnaire')
            else:
                error = True
    else:
        form = LoginForm()
    return render(request, "gestion_utilisateurs/login.html", {'form': form, 'error': error})


@login_required
def dashboard_admin(request):
    if not hasattr(request.user, 'administrateur'):
        return redirect('login')

    liste_gestionnaires = Gestionnaire.objects.all()
    total_des_gestionnaires = Gestionnaire.objects.count()
    gestionnaires_actif = Gestionnaire.objects.filter(is_active=True).count()
    gestionnaires_inactif = Gestionnaire.objects.filter(is_active=False).count()

    mouvements = Mouvement.objects.all().order_by('-date_operation')
    planifications = Mouvement.objects.filter(type_operation='emprunt', etat="PLANIFIE").order_by('-date_operation')
    emprunts_en_cours = Mouvement.objects.filter(type_operation='emprunt', etat="EN_COURS")
    emprunts_valide = Mouvement.objects.filter(type_operation='emprunt', etat="VALIDE")
    emprunts_refuse = Mouvement.objects.filter(type_operation='emprunt', etat="REFUSE")

    nb_inventaires_en_cours = Inventaire.objects.filter(statut='en_cours').count()
    dernier_inventaire = Inventaire.objects.order_by('-date_creation').first()

    context = {
        'admin': request.user,
        'gestionnaires': liste_gestionnaires,
        'total_gestionnaires': total_des_gestionnaires,
        'gestionnaires_actif': gestionnaires_actif,
        'gestionnaires_inactif': gestionnaires_inactif,
        'mouvements': mouvements,
        'planifications': planifications,
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_valide': emprunts_valide,
        'emprunts_refuse': emprunts_refuse,
        'nb_inventaires_en_cours': nb_inventaires_en_cours,
        'dernier_inventaire': dernier_inventaire,
    }
    return render(request, 'gestion_utilisateurs/dashboard_admin.html', context)


@login_required
def dashboard_gestionnaire(request):
    if not hasattr(request.user, 'gestionnaire'):
        return redirect('login')

    try:
        from equipements.models import Equipement
        from contacts.models import Contact
        stats_eq = {
            'total': Equipement.objects.filter(est_actif=True).count(),
            'disponible': Equipement.objects.filter(etat='disponible', est_actif=True).count(),
            'emprunte': Equipement.objects.filter(etat='emprunte', est_actif=True).count(),
        }
        stats_ct = {'total': Contact.objects.filter(est_actif=True).count()}
    except Exception:
        stats_eq = {'total': 0, 'disponible': 0, 'emprunte': 0}
        stats_ct = {'total': 0}

    context = {
        'gestionnaire': request.user,
        'stats_eq': stats_eq,
        'stats_ct': stats_ct,
    }
    return render(request, 'gestion_utilisateurs/dashboard_gestionnaire.html', context)


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def add_gestionnaire(request):
    if request.method == 'POST':
        form = GestionnaireCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Le gestionnaire {user.username} a été créé.")
            return redirect('dashboard_admin')
        else:
            messages.error(request, "Erreur lors de la création.")
    else:
        form = GestionnaireCreationForm()
    return render(request, 'gestion_utilisateurs/add_gestionnaire.html', {'form': form})


@login_required
def toggle_status(request, gest_id):
    if request.method == 'POST':
        gestionnaire = Gestionnaire.objects.get(id=gest_id)
        gestionnaire.is_active = not gestionnaire.is_active
        gestionnaire.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def modifier_mot_de_passe(request):
    if request.method == 'POST':
        form = ModifierMotDePasseForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Mot de passe modifié avec succès.")
            if request.user.is_staff:
                return redirect('dashboard_admin')
            return redirect('dashboard_gestionnaire')
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = ModifierMotDePasseForm(request.user)
    return render(request, 'gestion_utilisateurs/modifier_mot_de_passe.html', {'form': form})


@login_required
def loan_list(request):
    mouvements = Mouvement.objects.filter(type_operation='emprunt').order_by('-date_operation')
    return render(request, 'gestion_utilisateurs/listeA.html', {'emprunts': mouvements})


@login_required
def loan_planning(request):
    planifications = Mouvement.objects.filter(type_operation='emprunt', etat="PLANIFIE")
    return render(request, 'gestion_utilisateurs/planificationsA.html', {'planifications': planifications})


@login_required
def valider_planification(request, pk):
    if not hasattr(request.user, 'administrateur'):
        return redirect('dashboard_gestionnaire')
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.etat = "VALIDE"
    mouvement.message_admin = "Votre emprunt a été validé par l'administrateur."
    mouvement.save()
    return redirect('liste_planifications')


@login_required
def refuser_planification(request, pk):
    if not hasattr(request.user, 'administrateur'):
        return redirect('dashboard_gestionnaire')
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.etat = "REFUSE"
    mouvement.message_admin = "Votre emprunt a été refusé par l'administrateur."
    mouvement.save()
    return redirect('liste_planifications')


@login_required
def passer_en_cours(request, pk):
    if not hasattr(request.user, 'administrateur'):
        return redirect('dashboard_gestionnaire')
    mouvement = get_object_or_404(Mouvement, pk=pk)
    mouvement.etat = "EN_COURS"
    mouvement.save()
    return redirect('liste_planifications')