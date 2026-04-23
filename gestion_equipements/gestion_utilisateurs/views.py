from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, GestionnaireCreationForm, ModifierMotDePasseForm
from .models import Administrateur, Gestionnaire
from django.http import JsonResponse


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

    return render(request, "gestion_utilisateurs/login.html",{'form':form, 'error':error})


@login_required
def dashboard_admin(request):
    # (Grâce à mon héritage, je vérifie s'il existe dans la table Administrateur)
    if not hasattr(request.user, 'administrateur'):
        return redirect('login') 
        
    # On récupère tous les gestionnaires pour les afficher
    liste_gestionnaires = Gestionnaire.objects.all()
    total_des_gestionnaires = Gestionnaire.objects.count()
    gestionnaires_actif = Gestionnaire.objects.filter(is_active = True).count()
    gestionnaires_inactif = Gestionnaire.objects.filter(is_active = False).count()
    context = {
        'admin': request.user,
        'gestionnaires': liste_gestionnaires,
        'total_gestionnaires': total_des_gestionnaires,
        'gestionnaires_actif' : gestionnaires_actif,
        'gestionnaires_inactif' : gestionnaires_inactif
    }
    return render(request, 'gestion_utilisateurs/dashboard_admin.html', context)


@login_required
def dashboard_gestionnaire(request):
    if not hasattr(request.user, 'gestionnaire'):
        return redirect('login')
    
    # Import stats dynamiquement pour éviter circular imports
    try:
        from equipements.models import Equipement
        from contacts.models import Contact
        stats_eq = {
            'total': Equipement.objects.filter(est_actif=True).count(),
            'disponible': Equipement.objects.filter(etat='disponible', est_actif=True).count(),
            'emprunte': Equipement.objects.filter(etat='emprunte', est_actif=True).count(),
        }
        stats_ct = {
            'total': Contact.objects.filter(est_actif=True).count(),
        }
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
    logout(request) # Détruit la session 
    return redirect('index')


@login_required
def add_gestionnaire(request):
    # Vérification sécurité
    if not request.user.role != 'Administrateur':
        return redirect('dashboard_admin')
    
    # Traitement du formulaire
    if request.method == 'POST':
        form = GestionnaireCreationForm(request.POST)
        if form.is_valid():
            # Sauvegarde
            user = form.save()  
            messages.success(request, f"Le gestionnaire {user.username} a été créé et l'email envoyé.")   
            return redirect('dashboard_admin')
        else:
            messages.error(request, "Erreur lors de la création. Vérifiez les champs.")
    else:
        form = GestionnaireCreationForm()
    return render(request, 'gestion_utilisateurs/add_gestionnaire.html', {'form': form})


@login_required
def toggle_status(request, gest_id):
    if request.method == 'POST':
        gestionnaire = Gestionnaire.objects.get(id = gest_id)
        gestionnaire.is_active = not gestionnaire.is_active
        gestionnaire.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status':'error'}, status=400)


@login_required
def modifier_mot_de_passe(request):
    if request.method == 'POST':
        form = ModifierMotDePasseForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            # Garde la session active après changement MDP
            update_session_auth_hash(request, request.user)
            messages.success(request, "Votre mot de passe a été modifié avec succès.")
            if request.user.is_staff:
                return redirect('dashboard_admin')
            return redirect('dashboard_gestionnaire')
        else:
            messages.error(request, "Erreur lors de la modification. Vérifiez les champs.")
    else:
        form = ModifierMotDePasseForm(request.user)
    return render(request, 'gestion_utilisateurs/modifier_mot_de_passe.html', {'form': form})