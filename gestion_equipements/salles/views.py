# salles/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Salle
from .forms import SalleForm

@login_required
def liste_salles(request):
    salles = Salle.objects.filter(est_active=True)
    stats = {
        'total': salles.count(),
        'laboratoires': salles.filter(type_salle='laboratoire').count(),
        'salles_cours': salles.filter(type_salle='salle_cours').count(),
    }
    return render(request, 'salles/liste.html', {'salles': salles, 'stats': stats})

@login_required
def detail_salle(request, pk):
    salle = get_object_or_404(Salle, pk=pk)
    # Tous les équipements actuellement dans cette salle
    # equipements = salle.equipements.filter(est_actif=True)
    equipements = []
    return render(request, 'salles/detail.html', {
        'salle': salle,
        'equipements': equipements
    })

@login_required
def creer_salle(request):
    if request.method == 'POST':
        form = SalleForm(request.POST)
        if form.is_valid():
            salle = form.save()
            messages.success(request, f"La salle « {salle.nom} » a été créée.")
            return redirect('salles:liste_salles')
    else:
        form = SalleForm()
    return render(request, 'salles/form.html', {'form': form, 'titre': 'Ajouter une salle'})

@login_required
def modifier_salle(request, pk):
    salle = get_object_or_404(Salle, pk=pk)
    if request.method == 'POST':
        form = SalleForm(request.POST, instance=salle)
        if form.is_valid():
            form.save()
            messages.success(request, f"La salle « {salle.nom} » a été modifiée.")
            return redirect('salles:detail_salle', pk=pk)
    else:
        form = SalleForm(instance=salle)
    return render(request, 'salles/form.html', {'form': form, 'titre': 'Modifier la salle'})

@login_required
def supprimer_salle(request, pk):
    salle = get_object_or_404(Salle, pk=pk)
    if request.method == 'POST':
        salle.est_active = False
        salle.save()
        messages.success(request, f"La salle « {salle.nom} » a été supprimée.")
        return redirect('salles:liste_salles')
    return render(request, 'salles/confirmer_suppression.html', {'objet': salle, 'type': 'salle'})