"""
Module Statistiques — Vues principales
Fournit :
  - tableau de bord statistique global
  - données JSON pour les graphiques (Chart.js)
  - filtrage avancé multi-critères des équipements et mouvements
"""

import json
from datetime import date, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from equipements.models import Equipement, Categorie
from contacts.models import Contact
from emprunt.models import Mouvement


# ──────────────────────────────────────────────────────────────────────────────
# 1. TABLEAU DE BORD STATISTIQUE PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def tableau_bord_statistiques(request):
    # ── KPI équipements ──────────────────────────────────────────────────────
    total_eq          = Equipement.objects.filter(est_actif=True).count()
    total_disponible  = Equipement.objects.filter(etat='disponible', est_actif=True).count()
    total_emprunte    = Equipement.objects.filter(etat='emprunte', est_actif=True).count()
    total_maintenance = Equipement.objects.filter(etat='maintenance', est_actif=True).count()
    total_retire      = Equipement.objects.filter(est_actif=False).count()
    total_categories  = Categorie.objects.count()

    # ── KPI contacts ─────────────────────────────────────────────────────────
    total_contacts      = Contact.objects.filter(est_actif=True).count()
    contacts_etudiant   = Contact.objects.filter(type_contact='etudiant', est_actif=True).count()
    contacts_enseignant = Contact.objects.filter(type_contact='enseignant', est_actif=True).count()
    contacts_personnel  = Contact.objects.filter(type_contact='personnel', est_actif=True).count()
    contacts_externe    = Contact.objects.filter(type_contact='externe', est_actif=True).count()

    # ── KPI mouvements ────────────────────────────────────────────────────────
    aujourd_hui = date.today()

    total_mouvements   = Mouvement.objects.count()
    total_entrees      = Mouvement.objects.filter(type_operation='entree').count()
    total_emprunts     = Mouvement.objects.filter(type_operation='emprunt').count()
    total_sorties      = Mouvement.objects.filter(type_operation='sortie').count()

    emprunts_en_cours  = Mouvement.objects.filter(type_operation='emprunt', etat='EN_COURS').count()
    emprunts_retournes = Mouvement.objects.filter(type_operation='emprunt', etat='RETOURNE').count()
    emprunts_expires   = Mouvement.objects.filter(type_operation='emprunt', etat='EXPIRE').count()
    emprunts_annules   = Mouvement.objects.filter(type_operation='emprunt', etat='ANNULE').count()
    emprunts_planifies = Mouvement.objects.filter(type_operation='emprunt', etat='PLANIFIE').count()
    emprunts_valides   = Mouvement.objects.filter(type_operation='emprunt', etat='VALIDE').count()

    emprunts_en_retard = Mouvement.objects.filter(
        type_operation='emprunt',
        etat='EN_COURS',
        date_retour_prevu__lt=aujourd_hui
    ).count()

    # ── Taux de disponibilité ─────────────────────────────────────────────────
    taux_dispo = round((total_disponible / total_eq * 100), 1) if total_eq > 0 else 0

    # ── Top 5 catégories ──────────────────────────────────────────────────────
    top_categories = (
        Categorie.objects
        .annotate(nb=Count('equipements', filter=Q(equipements__est_actif=True)))
        .order_by('-nb')[:5]
    )

    # ── Top 5 emprunteurs ─────────────────────────────────────────────────────
    top_emprunteurs = (
        Contact.objects
        .annotate(nb_emprunts=Count('mouvement'))
        .order_by('-nb_emprunts')[:5]
    )

    # ── Mouvements des 6 derniers mois (par mois) ─────────────────────────────
    six_mois_avant = aujourd_hui - timedelta(days=180)
    emprunts_par_mois = (
        Mouvement.objects
        .filter(type_operation='emprunt', date_operation__gte=six_mois_avant)
        .annotate(mois=TruncMonth('date_operation'))
        .values('mois')
        .annotate(nb=Count('id'))
        .order_by('mois')
    )
    labels_mois = [e['mois'].strftime('%b %Y') for e in emprunts_par_mois]
    data_mois   = [e['nb'] for e in emprunts_par_mois]

    # ── Répartition emprunts par état ─────────────────────────────────────────
    etats_emprunts = {
        'En cours':  emprunts_en_cours,
        'Retourné':  emprunts_retournes,
        'Expiré':    emprunts_expires,
        'Annulé':    emprunts_annules,
        'Planifié':  emprunts_planifies,
        'Validé':    emprunts_valides,
    }

    context = {
        # KPI équipements
        'total_eq': total_eq,
        'total_disponible': total_disponible,
        'total_emprunte': total_emprunte,
        'total_maintenance': total_maintenance,
        'total_retire': total_retire,
        'total_categories': total_categories,
        'taux_dispo': taux_dispo,
        # KPI contacts
        'total_contacts': total_contacts,
        'contacts_etudiant': contacts_etudiant,
        'contacts_enseignant': contacts_enseignant,
        'contacts_personnel': contacts_personnel,
        'contacts_externe': contacts_externe,
        # KPI mouvements
        'total_mouvements': total_mouvements,
        'total_entrees': total_entrees,
        'total_emprunts': total_emprunts,
        'total_sorties': total_sorties,
        'emprunts_en_cours': emprunts_en_cours,
        'emprunts_retournes': emprunts_retournes,
        'emprunts_expires': emprunts_expires,
        'emprunts_en_retard': emprunts_en_retard,
        'emprunts_annules': emprunts_annules,
        'emprunts_planifies': emprunts_planifies,
        'emprunts_valides': emprunts_valides,
        # Listes
        'top_categories': top_categories,
        'top_emprunteurs': top_emprunteurs,
        # Données JSON pour Chart.js
        'labels_mois_json': json.dumps(labels_mois),
        'data_mois_json':   json.dumps(data_mois),
        'etats_labels_json': json.dumps(list(etats_emprunts.keys())),
        'etats_data_json':   json.dumps(list(etats_emprunts.values())),
    }
    return render(request, 'statistiques/tableau_bord.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# 2. APIs JSON POUR GRAPHIQUES
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def api_graphique_equipements_etat(request):
    data = (
        Equipement.objects.filter(est_actif=True)
        .values('etat').annotate(nb=Count('id')).order_by('etat')
    )
    labels_map = {'disponible': 'Disponible', 'emprunte': 'Emprunté',
                  'maintenance': 'Maintenance', 'retire': 'Retiré'}
    colors = {'disponible': '#56A361', 'emprunte': '#E07B39',
              'maintenance': '#E0C039', 'retire': '#601C1D'}
    return JsonResponse({
        'labels': [labels_map.get(d['etat'], d['etat']) for d in data],
        'data':   [d['nb'] for d in data],
        'colors': [colors.get(d['etat'], '#999') for d in data],
    })


@login_required
def api_graphique_equipements_categorie(request):
    data = (
        Categorie.objects
        .annotate(nb=Count('equipements', filter=Q(equipements__est_actif=True)))
        .filter(nb__gt=0).order_by('-nb')[:8]
    )
    return JsonResponse({
        'labels': [d.nom for d in data],
        'data':   [d.nb for d in data],
    })


@login_required
def api_graphique_emprunts_mois(request):
    un_an_avant = date.today() - timedelta(days=365)
    data = (
        Mouvement.objects
        .filter(type_operation='emprunt', date_operation__gte=un_an_avant)
        .annotate(mois=TruncMonth('date_operation'))
        .values('mois').annotate(nb=Count('id')).order_by('mois')
    )
    return JsonResponse({
        'labels': [d['mois'].strftime('%b %Y') for d in data],
        'data':   [d['nb'] for d in data],
    })


@login_required
def api_graphique_contacts_type(request):
    data = (
        Contact.objects.filter(est_actif=True)
        .values('type_contact').annotate(nb=Count('id')).order_by('type_contact')
    )
    labels_map = {'etudiant': 'Étudiant', 'enseignant': 'Enseignant',
                  'personnel': 'Personnel', 'externe': 'Externe'}
    colors = ['#56A361', '#3d7a48', '#B3DEB7', '#A5A5A5']
    result_list = list(data)
    return JsonResponse({
        'labels': [labels_map.get(d['type_contact'], d['type_contact']) for d in result_list],
        'data':   [d['nb'] for d in result_list],
        'colors': colors[:len(result_list)],
    })


# ──────────────────────────────────────────────────────────────────────────────
# 3. FILTRAGE AVANCÉ ÉQUIPEMENTS
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def filtrage_avance_equipements(request):
    q            = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '').strip()
    etat         = request.GET.get('etat', '').strip()
    localisation = request.GET.get('localisation', '').strip()
    date_debut   = request.GET.get('date_debut', '').strip()
    date_fin     = request.GET.get('date_fin', '').strip()
    actif        = request.GET.get('actif', 'true').strip()
    tri          = request.GET.get('tri', 'nom').strip()

    qs = Equipement.objects.select_related('categorie').prefetch_related('mouvements')

    if actif == 'false':
        qs = qs.filter(est_actif=False)
    elif actif != 'all':
        qs = qs.filter(est_actif=True)

    if q:
        qs = qs.filter(
            Q(nom__icontains=q) | Q(reference__icontains=q) |
            Q(description__icontains=q) | Q(notes__icontains=q)
        )
    if categorie_id:
        qs = qs.filter(categorie_id=categorie_id)
    if etat:
        qs = qs.filter(etat=etat)
    if localisation:
        qs = qs.filter(localisation__icontains=localisation)
    if date_debut:
        qs = qs.filter(date_acquisition__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_acquisition__lte=date_fin)

    TRI_OPTIONS = {
        'nom': 'nom', '-nom': '-nom',
        'date_ajout': 'date_ajout', '-date_ajout': '-date_ajout',
        'date_acquisition': 'date_acquisition',
        'etat': 'etat', 'categorie': 'categorie__nom',
    }
    qs = qs.order_by(TRI_OPTIONS.get(tri, 'nom'))

    context = {
        'equipements': qs,
        'categories': Categorie.objects.all().order_by('nom'),
        'stats_resultats': {
            'total': qs.count(),
            'disponible': qs.filter(etat='disponible').count(),
            'emprunte': qs.filter(etat='emprunte').count(),
            'maintenance': qs.filter(etat='maintenance').count(),
        },
        'q': q, 'categorie_id': categorie_id, 'etat': etat,
        'localisation': localisation, 'date_debut': date_debut,
        'date_fin': date_fin, 'actif': actif, 'tri': tri,
    }
    return render(request, 'statistiques/filtrage_equipements.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# 4. FILTRAGE AVANCÉ MOUVEMENTS (ancien "emprunts")
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def filtrage_avance_emprunts(request):
    q            = request.GET.get('q', '').strip()
    type_op      = request.GET.get('type_operation', '').strip()
    etat         = request.GET.get('etat', '').strip()
    date_debut   = request.GET.get('date_debut', '').strip()
    date_fin     = request.GET.get('date_fin', '').strip()
    retour_debut = request.GET.get('retour_debut', '').strip()
    retour_fin   = request.GET.get('retour_fin', '').strip()
    en_retard    = request.GET.get('en_retard', '').strip()
    tri          = request.GET.get('tri', '-date_operation').strip()

    aujourd_hui = date.today()
    qs = Mouvement.objects.select_related('beneficiaire', 'equipement', 'gestionnaire')

    if q:
        qs = qs.filter(
            Q(beneficiaire__nom__icontains=q) |
            Q(beneficiaire__prenom__icontains=q) |
            Q(beneficiaire__matricule__icontains=q) |
            Q(beneficiaire__email__icontains=q) |
            Q(objet_demande__icontains=q) |
            Q(equipement__nom__icontains=q)
        )
    if type_op:
        qs = qs.filter(type_operation=type_op)
    if etat:
        qs = qs.filter(etat=etat)
    if date_debut:
        qs = qs.filter(date_operation__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_operation__lte=date_fin)
    if retour_debut:
        qs = qs.filter(date_retour_prevu__gte=retour_debut)
    if retour_fin:
        qs = qs.filter(date_retour_prevu__lte=retour_fin)
    if en_retard == '1':
        qs = qs.filter(type_operation='emprunt', etat='EN_COURS',
                       date_retour_prevu__lt=aujourd_hui)

    TRI_OPTIONS = {
        '-date_operation': '-date_operation', 'date_operation': 'date_operation',
        'date_retour_prevu': 'date_retour_prevu',
        'etat': 'etat', 'beneficiaire': 'beneficiaire__nom',
    }
    qs = qs.order_by(TRI_OPTIONS.get(tri, '-date_operation'))

    context = {
        'mouvements': qs,
        'stats_resultats': {
            'total': qs.count(),
            'en_cours': qs.filter(etat='EN_COURS').count(),
            'retournes': qs.filter(etat='RETOURNE').count(),
            'en_retard': qs.filter(type_operation='emprunt', etat='EN_COURS',
                                   date_retour_prevu__lt=aujourd_hui).count(),
            'expires': qs.filter(etat='EXPIRE').count(),
        },
        'types_operation': Mouvement.TYPE_OPERATION_CHOICES,
        'etats': Mouvement.ETAT_CHOICES,
        'aujourd_hui': aujourd_hui,
        'q': q, 'type_operation': type_op, 'etat': etat,
        'date_debut': date_debut, 'date_fin': date_fin,
        'retour_debut': retour_debut, 'retour_fin': retour_fin,
        'en_retard': en_retard, 'tri': tri,
    }
    return render(request, 'statistiques/filtrage_emprunts.html', context)