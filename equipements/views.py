from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import openpyxl

from .models import Equipement, Categorie
from .forms import EquipementForm, CategorieForm, ImportExcelForm


@login_required
def liste_equipements(request):
    """Affiche la liste des équipements avec recherche et filtre par catégorie."""
    query = request.GET.get('q', '')
    categorie_id = request.GET.get('categorie', '')
    etat = request.GET.get('etat', '')

    equipements = Equipement.objects.filter(est_actif=True)

    if query:
        equipements = equipements.filter(
            Q(nom__icontains=query) | Q(reference__icontains=query)
        )
    if categorie_id:
        equipements = equipements.filter(categorie_id=categorie_id)
    if etat:
        equipements = equipements.filter(etat=etat)

    categories = Categorie.objects.all()
    stats = {
        'total': Equipement.objects.filter(est_actif=True).count(),
        'disponible': Equipement.objects.filter(etat='disponible', est_actif=True).count(),
        'emprunte': Equipement.objects.filter(etat='emprunte', est_actif=True).count(),
        'maintenance': Equipement.objects.filter(etat='maintenance', est_actif=True).count(),
    }

    context = {
        'equipements': equipements,
        'categories': categories,
        'query': query,
        'categorie_id': categorie_id,
        'etat_filtre': etat,
        'stats': stats,
    }
    return render(request, 'equipements/liste.html', context)


@login_required
def detail_equipement(request, pk):
    """Affiche la fiche détaillée d'un équipement."""
    equipement = get_object_or_404(Equipement, pk=pk)
    return render(request, 'equipements/detail.html', {'equipement': equipement})


@login_required
def creer_equipement(request):
    """Crée un nouvel équipement."""
    if request.method == 'POST':
        form = EquipementForm(request.POST, request.FILES)
        if form.is_valid():
            equipement = form.save()
            messages.success(request, f"L'équipement « {equipement.nom} » a été créé avec succès.")
            return redirect('liste_equipements')
        else:
            messages.error(request, "Erreur lors de la création. Vérifiez les champs.")
    else:
        form = EquipementForm()
    return render(request, 'equipements/form.html', {'form': form, 'action': 'Créer', 'titre': 'Ajouter un équipement'})


@login_required
def modifier_equipement(request, pk):
    """Modifie un équipement existant."""
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        form = EquipementForm(request.POST, request.FILES, instance=equipement)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'équipement « {equipement.nom} » a été modifié.")
            return redirect('detail_equipement', pk=pk)
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = EquipementForm(instance=equipement)
    return render(request, 'equipements/form.html', {'form': form, 'action': 'Modifier', 'titre': 'Modifier l\'équipement', 'equipement': equipement})


@login_required
def retirer_equipement(request, pk):
    """Retire (désactive) un équipement."""
    equipement = get_object_or_404(Equipement, pk=pk)
    if request.method == 'POST':
        equipement.est_actif = False
        equipement.etat = 'retire'
        equipement.save()
        messages.success(request, f"L'équipement « {equipement.nom} » a été retiré.")
        return redirect('liste_equipements')
    return render(request, 'equipements/confirmer_suppression.html', {'objet': equipement, 'type': 'équipement'})


@login_required
def importer_equipements(request):
    """Importe des équipements depuis un fichier Excel."""
    if request.method == 'POST':
        form = ImportExcelForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier_excel']
            try:
                wb = openpyxl.load_workbook(fichier)
                ws = wb.active
                nb_crees = 0
                nb_erreurs = 0
                erreurs = []

                # Lecture des lignes (skip header row 1)
                for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    try:
                        nom = str(row[0]).strip() if row[0] else ''
                        reference = str(row[1]).strip() if row[1] else ''
                        nom_categorie = str(row[2]).strip() if row[2] else ''
                        description = str(row[3]).strip() if row[3] else ''
                        etat = str(row[4]).strip().lower() if row[4] else 'disponible'
                        localisation = str(row[5]).strip() if row[5] else ''

                        if not nom:
                            erreurs.append(f"Ligne {i}: nom manquant")
                            nb_erreurs += 1
                            continue

                        # Etat valide
                        etats_valides = ['disponible', 'emprunte', 'maintenance', 'retire']
                        if etat not in etats_valides:
                            etat = 'disponible'

                        # Catégorie
                        categorie = None
                        if nom_categorie:
                            categorie, _ = Categorie.objects.get_or_create(nom=nom_categorie)

                        # Référence unique
                        if reference and Equipement.objects.filter(reference=reference).exists():
                            erreurs.append(f"Ligne {i}: référence « {reference} » déjà existante, ignorée")
                            nb_erreurs += 1
                            continue

                        Equipement.objects.create(
                            nom=nom,
                            reference=reference,
                            categorie=categorie,
                            description=description,
                            etat=etat,
                            localisation=localisation,
                        )
                        nb_crees += 1
                    except Exception as e:
                        erreurs.append(f"Ligne {i}: {str(e)}")
                        nb_erreurs += 1

                msg = f"{nb_crees} équipement(s) importé(s) avec succès."
                if nb_erreurs:
                    msg += f" {nb_erreurs} ligne(s) ignorée(s)."
                messages.success(request, msg)
                for err in erreurs[:5]:
                    messages.warning(request, err)
                return redirect('liste_equipements')

            except Exception as e:
                messages.error(request, f"Erreur lors de la lecture du fichier : {str(e)}")
        else:
            messages.error(request, "Fichier invalide.")
    else:
        form = ImportExcelForm()
    return render(request, 'equipements/importer.html', {'form': form})
