from django.shortcuts import render, get_object_or_404, redirect
#from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import Emprunt
from .forms  import EmpruntModificationForm


# ── Helpers permission ────────────────────────────────────────────────────────

def verifier_admin(user):
    """Bloque l'accès si l'utilisateur n'est pas ADMIN."""
    if not user.is_authenticated or user.role != 'ADMIN':
        raise PermissionDenied

def verifier_staff(user):
    """Bloque l'accès si l'utilisateur n'est ni ADMIN ni GEST."""
    if not user.is_authenticated or user.role not in ('ADMIN', 'GEST'):
        raise PermissionDenied


# ── Liste des emprunts ────────────────────────────────────────────────────────

#@login_required
def liste_emprunts(request):
    emprunts = Emprunt.objects.select_related('beneficiaire').prefetch_related('equipements').all()
    return render(request, 'emprunts/liste_emprunts.html', {'emprunts': emprunts})


# ── Modification limitée (RG.04) ──────────────────────────────────────────────

#@login_required
def modifier_emprunt(request, pk):
    """Seuls date_emprunt et beneficiaire peuvent être modifiés."""
    verifier_staff(request.user)
    emprunt = get_object_or_404(Emprunt, pk=pk)

    if request.method == 'POST':
        form = EmpruntModificationForm(request.POST, instance=emprunt)
        if form.is_valid():
            form.save()
            messages.success(request, f"Emprunt #{pk} modifié avec succès.")
            return redirect('liste_emprunts')
        else:
            messages.error(request, "Erreur dans le formulaire.")
    else:
        form = EmpruntModificationForm(instance=emprunt)

    return render(request, 'emprunts/modifier_emprunt.html', {
        'form': form,
        'emprunt': emprunt,
    })


# ── Validation admin (RG.03) ──────────────────────────────────────────────────

#@login_required
def liste_emprunts_planifies(request):
    """Liste des emprunts planifiés en attente — réservé ADMIN."""
    verifier_admin(request.user)
    emprunts = (
        Emprunt.objects
        .filter(type_emprunt='PLANIFIE', statut='EN_ATTENTE')
        .select_related('beneficiaire', 'cree_par')
        .prefetch_related('equipements')
    )
    return render(request, 'emprunts/emprunts_planifies.html', {'emprunts': emprunts})


#@login_required
def valider_emprunt(request, pk):
    """L'admin valide un emprunt planifié."""
    verifier_admin(request.user)
    emprunt = get_object_or_404(Emprunt, pk=pk)

    if request.method == 'POST':
        try:
            emprunt.valider_emprunt(admin_user=request.user)
            messages.success(request, f"✔ Emprunt #{pk} validé avec succès.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('liste_emprunts_planifies')

    return render(request, 'emprunts/confirmer_validation.html', {'emprunt': emprunt})


#@login_required
def rejeter_emprunt(request, pk):
    """L'admin rejette un emprunt planifié."""
    verifier_admin(request.user)
    emprunt = get_object_or_404(Emprunt, pk=pk)

    if request.method == 'POST':
        try:
            emprunt.rejeter_emprunt()
            messages.warning(request, f"✘ Emprunt #{pk} rejeté.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('liste_emprunts_planifies')

    return render(request, 'emprunts/confirmer_rejet.html', {'emprunt': emprunt})
