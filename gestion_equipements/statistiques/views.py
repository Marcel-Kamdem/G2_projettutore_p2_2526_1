"""
Module Statistiques — Vues principales
Fournit :
  - tableau de bord statistique global
  - données JSON pour les graphiques (Chart.js)
  - filtrage avancé multi-critères des équipements et emprunts
"""

import json
from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncWeek

from equipements.models import Equipement, Categorie
from contacts.models import Contact
from emprunt.models import Emprunt


# ──────────────────────────────────────────────────────────────────────────────
# 1. TABLEAU DE BORD STATISTIQUE PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def tableau_bord_statistiques(request):
    """
    Vue principale : KPI globaux + données pour graphiques Chart.js
    Accessible via GET /statistiques/
    """

    # ── KPI équipements ──────────────────────────────────────────────────────
    total_eq         = Equipement.objects.filter(est_actif=True).count()
    total_disponible = Equipement.objects.filter(etat='disponible', est_actif=True).count()
    total_emprunte   = Equipement.objects.filter(etat='emprunte',   est_actif=True).count()
    total_maintenance= Equipement.objects.filter(etat='maintenance',est_actif=True).count()
    total_retire     = Equipement.objects.filter(est_actif=False).count()
    total_categories = Categorie.objects.count()

    # ── KPI contacts ─────────────────────────────────────────────────────────
    total_contacts   = Contact.objects.filter(est_actif=True).count()
    contacts_etudiant  = Contact.objects.filter(type_contact='etudiant',   est_actif=True).count()
    contacts_enseignant= Contact.objects.filter(type_contact='enseignant', est_actif=True).count()
    contacts_personnel = Contact.objects.filter(type_contact='personnel',  est_actif=True).count()
    contacts_externe   = Contact.objects.filter(type_contact='externe',    est_actif=True).count()

    # ── KPI emprunts ──────────────────────────────────────────────────────────
    total_emprunts      = Emprunt.objects.count()
    emprunts_en_cours   = Emprunt.objects.filter(etat='En cours').count()
    emprunts_retournes  = Emprunt.objects.filter(etat='Retourné').count()
    emprunts_expires    = Emprunt.objects.filter(etat='Expiré').count()
    emprunts_annules    = Emprunt.objects.filter(etat='Annulé').count()
    emprunts_planifies  = Emprunt.objects.filter(etat='Planifié').count()
    emprunts_valides    = Emprunt.objects.filter(etat='Validé').count()

    # Emprunts en retard (date_retour_prevu dépassée, pas encore retournés)
    aujourd_hui = date.today()
    emprunts_en_retard = Emprunt.objects.filter(
        etat='En cours',
        date_retour_prevu__lt=aujourd_hui
    ).count()

    # ── Taux de disponibilité ─────────────────────────────────────────────────
    taux_dispo = round((total_disponible / total_eq * 100), 1) if total_eq > 0 else 0

    # ── Top 5 catégories par nombre d'équipements ────────────────────────────
    top_categories = (
        Categorie.objects
        .annotate(nb=Count('equipements', filter=Q(equipements__est_actif=True)))
        .order_by('-nb')[:5]
    )

    # ── Top 5 emprunteurs (contacts avec le plus d'emprunts) ─────────────────
    top_emprunteurs = (
        Contact.objects
        .annotate(nb_emprunts=Count('emprunt'))
        .order_by('-nb_emprunts')[:5]
    )

    # ── Emprunts des 6 derniers mois (par mois) ───────────────────────────────
    six_mois_avant = aujourd_hui - timedelta(days=180)
    emprunts_par_mois = (
        Emprunt.objects
        .filter(date_empr__gte=six_mois_avant)
        .annotate(mois=TruncMonth('date_empr'))
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

        # KPI emprunts
        'total_emprunts': total_emprunts,
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

        # Données graphiques sérialisées JSON pour Chart.js
        'labels_mois_json':    json.dumps(labels_mois),
        'data_mois_json':      json.dumps(data_mois),
        'etats_labels_json':   json.dumps(list(etats_emprunts.keys())),
        'etats_data_json':     json.dumps(list(etats_emprunts.values())),
    }

    return render(request, 'statistiques/tableau_bord.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# 2. DONNÉES JSON POUR GRAPHIQUES AJAX (Chart.js)
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def api_graphique_equipements_etat(request):
    """
    JSON : répartition des équipements actifs par état.
    GET /statistiques/api/equipements-etat/
    """
    data = (
        Equipement.objects
        .filter(est_actif=True)
        .values('etat')
        .annotate(nb=Count('id'))
        .order_by('etat')
    )
    labels_map = {
        'disponible':  'Disponible',
        'emprunte':    'Emprunté',
        'maintenance': 'Maintenance',
        'retire':      'Retiré',
    }
    colors = {
        'disponible':  '#56A361',
        'emprunte':    '#E07B39',
        'maintenance': '#E0C039',
        'retire':      '#601C1D',
    }
    result = {
        'labels': [labels_map.get(d['etat'], d['etat']) for d in data],
        'data':   [d['nb'] for d in data],
        'colors': [colors.get(d['etat'], '#999') for d in data],
    }
    return JsonResponse(result)


@login_required
def api_graphique_equipements_categorie(request):
    """
    JSON : nombre d'équipements par catégorie (top 8).
    GET /statistiques/api/equipements-categorie/
    """
    data = (
        Categorie.objects
        .annotate(nb=Count('equipements', filter=Q(equipements__est_actif=True)))
        .filter(nb__gt=0)
        .order_by('-nb')[:8]
    )
    result = {
        'labels': [d.nom for d in data],
        'data':   [d.nb for d in data],
    }
    return JsonResponse(result)


@login_required
def api_graphique_emprunts_mois(request):
    """
    JSON : nombre d'emprunts par mois sur les 12 derniers mois.
    GET /statistiques/api/emprunts-mois/
    """
    un_an_avant = date.today() - timedelta(days=365)
    data = (
        Emprunt.objects
        .filter(date_empr__gte=un_an_avant)
        .annotate(mois=TruncMonth('date_empr'))
        .values('mois')
        .annotate(nb=Count('id'))
        .order_by('mois')
    )
    result = {
        'labels': [d['mois'].strftime('%b %Y') for d in data],
        'data':   [d['nb'] for d in data],
    }
    return JsonResponse(result)


@login_required
def api_graphique_contacts_type(request):
    """
    JSON : répartition des contacts actifs par type.
    GET /statistiques/api/contacts-type/
    """
    data = (
        Contact.objects
        .filter(est_actif=True)
        .values('type_contact')
        .annotate(nb=Count('id'))
        .order_by('type_contact')
    )
    labels_map = {
        'etudiant':   'Étudiant',
        'enseignant': 'Enseignant',
        'personnel':  'Personnel',
        'externe':    'Externe',
    }
    colors = ['#56A361', '#3d7a48', '#B3DEB7', '#A5A5A5']
    result = {
        'labels': [labels_map.get(d['type_contact'], d['type_contact']) for d in data],
        'data':   [d['nb'] for d in data],
        'colors': colors[:len(list(data))],
    }
    return JsonResponse(result)


# ──────────────────────────────────────────────────────────────────────────────
# 3. FILTRAGE AVANCÉ ÉQUIPEMENTS
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def filtrage_avance_equipements(request):
    """
    Filtrage multi-critères des équipements.
    Critères : nom/référence, catégorie, état, date acquisition (plage),
               localisation, actif/inactif, tri.
    GET /statistiques/filtrage/equipements/
    """
    # Récupération des paramètres GET
    q            = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '').strip()
    etat         = request.GET.get('etat', '').strip()
    localisation = request.GET.get('localisation', '').strip()
    date_debut   = request.GET.get('date_debut', '').strip()
    date_fin     = request.GET.get('date_fin', '').strip()
    actif        = request.GET.get('actif', 'true').strip()
    tri          = request.GET.get('tri', 'nom').strip()

    # Queryset de base
    qs = Equipement.objects.select_related('categorie').prefetch_related('emprunts')

    # Filtre actif/inactif
    if actif == 'false':
        qs = qs.filter(est_actif=False)
    elif actif == 'all':
        pass  # pas de filtre
    else:
        qs = qs.filter(est_actif=True)

    # Recherche textuelle
    if q:
        qs = qs.filter(
            Q(nom__icontains=q) |
            Q(reference__icontains=q) |
            Q(description__icontains=q) |
            Q(notes__icontains=q)
        )

    # Filtre catégorie (clé étrangère — FK respectée)
    if categorie_id:
        qs = qs.filter(categorie_id=categorie_id)

    # Filtre état
    if etat:
        qs = qs.filter(etat=etat)

    # Filtre localisation
    if localisation:
        qs = qs.filter(localisation__icontains=localisation)

    # Plage de dates d'acquisition
    if date_debut:
        qs = qs.filter(date_acquisition__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_acquisition__lte=date_fin)

    # Tri
    TRI_OPTIONS = {
        'nom':              'nom',
        '-nom':             '-nom',
        'date_ajout':       'date_ajout',
        '-date_ajout':      '-date_ajout',
        'date_acquisition': 'date_acquisition',
        'etat':             'etat',
        'categorie':        'categorie__nom',
    }
    champ_tri = TRI_OPTIONS.get(tri, 'nom')
    qs = qs.order_by(champ_tri)

    categories = Categorie.objects.all().order_by('nom')

    # Stats sur les résultats filtrés
    stats_resultats = {
        'total':        qs.count(),
        'disponible':   qs.filter(etat='disponible').count(),
        'emprunte':     qs.filter(etat='emprunte').count(),
        'maintenance':  qs.filter(etat='maintenance').count(),
    }

    context = {
        'equipements':      qs,
        'categories':       categories,
        'stats_resultats':  stats_resultats,
        # Valeurs actuelles des filtres (pour pré-remplir le formulaire)
        'q':            q,
        'categorie_id': categorie_id,
        'etat':         etat,
        'localisation': localisation,
        'date_debut':   date_debut,
        'date_fin':     date_fin,
        'actif':        actif,
        'tri':          tri,
    }
    return render(request, 'statistiques/filtrage_equipements.html', context)


# ──────────────────────────────────────────────────────────────────────────────
# 4. FILTRAGE AVANCÉ EMPRUNTS
# ──────────────────────────────────────────────────────────────────────────────

@login_required
def filtrage_avance_emprunts(request):
    """
    Filtrage multi-critères des emprunts.
    Critères : bénéficiaire (nom/prénom/matricule), état, plage dates emprunt,
               plage dates retour, en retard, objet demandé, tri.
    GET /statistiques/filtrage/emprunts/
    """
    q            = request.GET.get('q', '').strip()
    etat         = request.GET.get('etat', '').strip()
    date_debut   = request.GET.get('date_debut', '').strip()
    date_fin     = request.GET.get('date_fin', '').strip()
    retour_debut = request.GET.get('retour_debut', '').strip()
    retour_fin   = request.GET.get('retour_fin', '').strip()
    en_retard    = request.GET.get('en_retard', '').strip()
    tri          = request.GET.get('tri', '-date_empr').strip()

    # Queryset de base — FK vers Contact respectée
    qs = Emprunt.objects.select_related('beneficiaire')

    # Recherche textuelle sur le bénéficiaire (FK Contact) et l'objet
    if q:
        qs = qs.filter(
            Q(beneficiaire__nom__icontains=q) |
            Q(beneficiaire__prenom__icontains=q) |
            Q(beneficiaire__matricule__icontains=q) |
            Q(beneficiaire__email__icontains=q) |
            Q(object_dmd__icontains=q)
        )

    # Filtre état
    if etat:
        qs = qs.filter(etat=etat)

    # Plage dates d'emprunt
    if date_debut:
        qs = qs.filter(date_empr__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_empr__lte=date_fin)

    # Plage dates de retour prévues
    if retour_debut:
        qs = qs.filter(date_retour_prevu__gte=retour_debut)
    if retour_fin:
        qs = qs.filter(date_retour_prevu__lte=retour_fin)

    # Filtre "en retard" (actifs dont la date prévue est dépassée)
    aujourd_hui = date.today()
    if en_retard == '1':
        qs = qs.filter(
            etat='En cours',
            date_retour_prevu__lt=aujourd_hui
        )

    # Tri
    TRI_OPTIONS = {
        '-date_empr':        '-date_empr',
        'date_empr':         'date_empr',
        'date_retour_prevu': 'date_retour_prevu',
        'etat':              'etat',
        'beneficiaire':      'beneficiaire__nom',
    }
    champ_tri = TRI_OPTIONS.get(tri, '-date_empr')
    qs = qs.order_by(champ_tri)

    # Stats sur les résultats filtrés
    stats_resultats = {
        'total':       qs.count(),
        'en_cours':    qs.filter(etat='En cours').count(),
        'retournes':   qs.filter(etat='Retourné').count(),
        'en_retard':   qs.filter(etat='En cours', date_retour_prevu__lt=aujourd_hui).count(),
        'expires':     qs.filter(etat='Expiré').count(),
    }

    ETATS_EMPRUNT = [
        ('En cours', 'En cours'),
        ('Planifié', 'Planifié'),
        ('Validé', 'Validé'),
        ('Retourné', 'Retourné'),
        ('Expiré', 'Expiré'),
        ('Annulé', 'Annulé'),
    ]

    context = {
        'emprunts':        qs,
        'stats_resultats': stats_resultats,
        'etats_emprunt':   ETATS_EMPRUNT,
        'aujourd_hui':     aujourd_hui,
        # Valeurs actuelles des filtres
        'q':            q,
        'etat':         etat,
        'date_debut':   date_debut,
        'date_fin':     date_fin,
        'retour_debut': retour_debut,
        'retour_fin':   retour_fin,
        'en_retard':    en_retard,
        'tri':          tri,
    }
    return render(request, 'statistiques/filtrage_emprunts.html', context)
