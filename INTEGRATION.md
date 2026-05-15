# Guide d'intégration — Module Statistiques

**Auteur :** Membre du groupe (partie Statistiques / Graphiques / Filtrage avancé)  
**Branche :** `feature/statistiques-filtrage`

---

## 1. Copier le dossier de l'app

Placer le dossier `statistiques/` dans le projet Django, au même niveau que les autres apps :

```
gestion_equipements/
├── contacts/
├── emprunt/
├── equipements/
├── gestion_equipements/
├── gestion_utilisateurs/
├── statistiques/          ← copier ici
└── manage.py
```

---

## 2. Ajouter l'app dans settings.py

Dans `gestion_equipements/gestion_equipements/settings.py`, ajouter `'statistiques'` dans `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    ...
    'gestion_utilisateurs',
    'equipements',
    'contacts',
    'emprunt',
    'statistiques',   # ← ajouter cette ligne
]
```

---

## 3. Ajouter l'URL dans urls.py

Dans `gestion_equipements/gestion_equipements/urls.py`, ajouter l'include :

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('statistiques/', include('statistiques.urls')),  # ← ajouter
]
```

---

## 4. Ajouter le lien dans le dashboard gestionnaire (optionnel mais recommandé)

Dans `gestion_utilisateurs/templates/gestion_utilisateurs/dashboard_gestionnaire.html`,
ajouter dans le `<nav>` et dans les actions rapides :

```html
<!-- Dans le nav header -->
<a href="{% url 'statistiques:tableau_bord' %}">📊 Statistiques</a>

<!-- Dans les actions rapides -->
<a href="{% url 'statistiques:tableau_bord' %}" class="btn btn-outline">📊 Statistiques</a>
```

---

## 5. Aucune migration nécessaire

L'app `statistiques` **n'a aucun modèle propre**.  
Elle lit uniquement les modèles existants : `Equipement`, `Categorie`, `Contact`, `Emprunt`.  
Toutes les clés primaires et étrangères sont respectées. Aucune modification de la base de données.

---

## 6. Dépendances

Aucune dépendance Python supplémentaire.  
Les graphiques utilisent **Chart.js** chargé via CDN dans le template (pas d'installation npm).

---

## 7. URLs disponibles après intégration

| URL | Nom | Description |
|-----|-----|-------------|
| `/statistiques/` | `statistiques:tableau_bord` | Tableau de bord KPI + graphiques |
| `/statistiques/filtrage/equipements/` | `statistiques:filtrage_equipements` | Filtrage avancé équipements |
| `/statistiques/filtrage/emprunts/` | `statistiques:filtrage_emprunts` | Filtrage avancé emprunts |
| `/statistiques/api/equipements-etat/` | `statistiques:api_eq_etat` | JSON pour graphique état |
| `/statistiques/api/equipements-categorie/` | `statistiques:api_eq_categorie` | JSON pour graphique catégories |
| `/statistiques/api/emprunts-mois/` | `statistiques:api_emprunts_mois` | JSON pour graphique mensuel |
| `/statistiques/api/contacts-type/` | `statistiques:api_contacts_type` | JSON pour graphique contacts |
