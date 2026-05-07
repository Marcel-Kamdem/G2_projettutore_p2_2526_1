from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Emprunt
from .forms import ModifierEmpruntForm


# ──────────────────────────────────────────────────────────────────────────────
# VUE du membre qui fait l'import Excel/CSV
# Commentée pour l'instant - sera décommentée quand son code sera mergé
# ──────────────────────────────────────────────────────────────────────────────
# from emprunt.emprunt_service import EmpruntService
# from emprunt.forms import ImportEmpruntForm
#
# def importer_emprunts_view(request):
#     form = ImportEmpruntForm()
#     contexte = {'form': form}
#     if request.method == 'POST':
#         form = ImportEmpruntForm(request.POST, request.FILES)
#         if form.is_valid():
#             fichier = request.FILES['fichier_excel']
#             succes, erreurs = EmpruntService.importer_depuis_excel(fichier)
#             contexte['form']    = form
#             contexte['succes']  = succes
#             contexte['erreurs'] = erreurs
#     return render(request, 'emprunt/importer.html', contexte)


# ──────────────────────────────────────────────────────────────────────────────
# VUE 1 : Liste de tous les emprunts
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def liste_emprunts(request):
    emprunts = Emprunt.objects.all().order_by('-date_empr')
    return render(request, 'emprunt/liste_emprunts.html', {'emprunts': emprunts})


# ──────────────────────────────────────────────────────────────────────────────
# VUE 2 : Modifier un emprunt (champs limités : date_empr + beneficiaire)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def modifier_emprunt(request, pk):
    """
    RG.04 – Seuls date_empr et beneficiaire peuvent être modifiés.
    Les équipements et l'objet de la demande sont affichés en lecture seule.
    """
    emprunt = get_object_or_404(Emprunt, pk=pk)

    if not emprunt.peut_etre_modifie():
        messages.error(request, "Cet emprunt ne peut plus être modifié (retourné, annulé ou expiré).")
        return redirect('liste_emprunts')

    if request.method == 'POST':
        form = ModifierEmpruntForm(request.POST, instance=emprunt)
        if form.is_valid():
            form.save()
            messages.success(request, "L'emprunt a bien été modifié.")
            return redirect('liste_emprunts')
    else:
        form = ModifierEmpruntForm(instance=emprunt)

    return render(request, 'emprunt/modifier_emprunt.html', {
        'form'   : form,
        'emprunt': emprunt,
    })


# ──────────────────────────────────────────────────────────────────────────────
# VUE 3 : Page admin – liste des emprunts en attente de validation
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def validation_admin(request):
    """
    Réservée à l'admin uniquement.
    Affiche les emprunts avec état 'En attente' ou 'Planifié'.
    """
    if not request.user.is_staff:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('liste_emprunts')

    emprunts_en_attente = Emprunt.objects.filter(
        etat__in=["En attente", "Planifié"]
    ).order_by('date_retour_prevu')

    return render(request, 'emprunt/validation_admin.html', {
        'emprunts': emprunts_en_attente,
    })


# ──────────────────────────────────────────────────────────────────────────────
# VUE 4 : Admin valide un emprunt
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def valider_emprunt(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('liste_emprunts')

    emprunt = get_object_or_404(Emprunt, pk=pk)
    ok = emprunt.valider_emprunt()

    if ok:
        messages.success(request, f"L'emprunt #{pk} a été validé.")
    else:
        messages.warning(request, f"L'emprunt #{pk} ne peut pas être validé (état actuel : {emprunt.etat}).")

    return redirect('validation_admin')


# ──────────────────────────────────────────────────────────────────────────────
# VUE 5 : Admin refuse un emprunt
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def refuser_emprunt(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('liste_emprunts')

    emprunt = get_object_or_404(Emprunt, pk=pk)
    ok = emprunt.refuser_emprunt()

    if ok:
        messages.success(request, f"L'emprunt #{pk} a été refusé.")
    else:
        messages.warning(request, f"L'emprunt #{pk} ne peut pas être refusé (état actuel : {emprunt.etat}).")

    return redirect('validation_admin')