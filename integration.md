# Guide d'intégration — Modification limitée & Validation admin
**Branche :** `feature/modification-emprunt-validation-admin`  
**Fonctionnalités :** RG.04 (modification limitée) + RG.03 (validation admin)

---

## Ce que cette branche ajoute au projet

Un nouveau dossier `gestion_emprunts/` avec ces fichiers :

```
gestion_emprunts/
├── __init__.py
├── apps.py
├── models.py        → Beneficiaire, Equipement, Emprunt + méthodes POO
├── forms.py         → formulaire restreint (RG.04)
├── views.py         → modifier, valider, rejeter
├── urls.py          → routes
├── admin.py         → interface admin Django
├── migrations/
│   └── __init__.py
└── templates/emprunts/
    ├── liste_emprunts.html
    ├── modifier_emprunt.html
    ├── emprunts_planifies.html
    ├── confirmer_validation.html
    └── confirmer_rejet.html
```

Et 2 modifications dans les fichiers existants :
- `gestion_equipements/settings.py` → ajout de `'gestion_emprunts'` dans `INSTALLED_APPS`
- `gestion_equipements/urls.py` → ajout de `path('emprunts/', include('gestion_emprunts.urls'))`

---

## Étapes pour intégrer cette branche dans votre projet

### 1. Récupérer la branche

```bash
git fetch origin
git checkout main
git pull origin main
git merge feature/modification-emprunt-validation-admin
```

### 2. Vérifier settings.py

Ouvrir `gestion_equipements/settings.py` et vérifier que `'gestion_emprunts'` est bien dans `INSTALLED_APPS` :

```python
INSTALLED_APPS = [
    ...
    'gestion_utilisateur',
    'gestion_emprunts',   # ← doit être présent
]
```

### 3. Vérifier urls.py

Ouvrir `gestion_equipements/urls.py` et vérifier :

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('gestion_utilisateur/', include('gestion_utilisateur.urls')),
    path('emprunts/', include('gestion_emprunts.urls')),   # ← doit être présent
]
```

### 4. Lancer les migrations

```bash
cd gestion_equipements
python manage.py makemigrations gestion_emprunts
python manage.py migrate
```

### 5. Tester

```bash
python manage.py runserver
```

| URL | Ce qu'on voit |
|---|---|
| `/emprunts/` | Liste des emprunts |
| `/emprunts/1/modifier/` | Formulaire de modification (date + bénéficiaire seulement) |
| `/emprunts/planifies/` | Liste admin des emprunts en attente (admin seulement) |

---

## En cas de conflit Git

### Conflit sur settings.py

Garder les deux lignes, comme ceci :

```python
INSTALLED_APPS = [
    ...
    'gestion_utilisateur',
    'votre_autre_app',      # ← votre app
    'gestion_emprunts',     # ← la mienne
]
```

### Conflit sur urls.py

Garder tous les path(), comme ceci :

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('gestion_utilisateur/', include('gestion_utilisateur.urls')),
    path('votre_route/', include('votre_app.urls')),   # ← votre route
    path('emprunts/', include('gestion_emprunts.urls')),   # ← la mienne
]
```

Après résolution du conflit :

```bash
git add gestion_equipements/settings.py
git add gestion_equipements/urls.py
git commit -m "fix: résolution conflit merge gestion_emprunts"
```

---

## Points importants

- Cette branche ne touche à **aucun fichier existant** sauf `settings.py` et `urls.py`
- Le modèle `Utilisateur` de `gestion_utilisateur` doit avoir le champ `role` avec les valeurs `'ADMIN'` et `'GEST'`
- Seul un utilisateur avec `role='ADMIN'` peut accéder à `/emprunts/planifies/`
- Un emprunt avec statut `RETOURNE`, `ANNULE` ou `EXPIRE` ne peut pas être modifié
