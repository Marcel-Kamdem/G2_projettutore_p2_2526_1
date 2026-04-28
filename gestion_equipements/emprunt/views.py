from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import EmpruntForm
from .models import Emprunt

@login_required
def creer_emprunt(request):
    if request.method == "POST":
        form = EmpruntForm(request.POST)
        if form.is_valid():
            emprunt = form.save(commit=False)
            emprunt.gestionnaire = request.user 
            emprunt.etat = 'En attente'       
            emprunt.save()
            return redirect('liste_emprunts')
    else:
        form = EmpruntForm()
    
    return render(request, 'emprunt/creer_emprunt.html', {'form': form})

@login_required
def liste_emprunts(request):
    emprunts = Emprunt.objects.all().order_by('-date_empr')
    return render(request, 'emprunt/liste_emprunts.html', {'emprunts': emprunts})

@login_required
def valider_emprunt(request, pk, action):
    if not request.user.is_staff:
        return redirect('liste_emprunts')
        
    emprunt = get_object_or_404(Emprunt, pk=pk)
    
    if action == 'accepter':
        emprunt.etat = 'Accepté'
    elif action == 'refuser':
        emprunt.etat = 'Refusé'
        
    emprunt.save()
    return redirect('liste_emprunts')
@login_required
def planification_admin(request):
    emprunts = Emprunt.objects.all().order_by('-date_empr')
    return render(request, 'emprunt/planification_admin.html', {'emprunts': emprunts})

@login_required
def planification_gestionnaire(request):
    emprunts = Emprunt.objects.filter(gestionnaire=request.user).order_by('-date_empr')
    return render(request, 'emprunt/planification_gestionnaire.html', {'emprunts': emprunts})

