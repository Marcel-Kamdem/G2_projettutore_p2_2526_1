# GestioLab — Guide d'installation

## ÉTAPE 1 — Prérequis
- Python 3.11+  →  https://www.python.org/downloads/
- MySQL 8.x     →  https://dev.mysql.com/downloads/installer/

## ÉTAPE 2 — Environnement virtuel
```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate
```

## ÉTAPE 3 — Installer les dépendances
```bash
pip install -r requirements.txt
```

## ÉTAPE 4 — Créer la base de données MySQL
```sql
CREATE DATABASE gestion_equipements_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## ÉTAPE 5 — Configurer le mot de passe MySQL
Ouvrez `gestion_equipements/gestion_equipements/settings.py` et modifiez :
```python
'PASSWORD': 'VOTRE_MOT_DE_PASSE_MYSQL',
```
(Si root sans mot de passe, laissez '')

## ÉTAPE 6 — Appliquer les migrations
```bash
cd gestion_equipements
python manage.py migrate
```

## ÉTAPE 7 — Créer l'administrateur
```bash
python manage.py shell
```
Puis dans le shell :
```python
from gestion_utilisateurs.models import Administrateur
admin = Administrateur(username='admin', email='admin@gestiolab.com', first_name='Admin', last_name='Principal', role='Admin', is_staff=True, is_superuser=True)
admin.set_password('Admin1234!')
admin.save()
exit()
```

## ÉTAPE 8 — Lancer le serveur
```bash
python manage.py runserver
```
→ Ouvrir : http://127.0.0.1:8000/

## Connexion
- Email : admin@gestiolab.com
- Mot de passe : Admin1234!

## URLs principales
| Page | URL |
|------|-----|
| Accueil | http://127.0.0.1:8000/ |
| Login | http://127.0.0.1:8000/authentification/ |
| Dashboard Gestionnaire | http://127.0.0.1:8000/dashboard-gestionnaire/ |
| Dashboard Admin | http://127.0.0.1:8000/dashboard-admin/ |
| Équipements | http://127.0.0.1:8000/equipements/ |
| Contacts | http://127.0.0.1:8000/contacts/ |
| Modifier MDP | http://127.0.0.1:8000/modifier-mot-de-passe/ |

## Format Excel — Équipements
Colonnes : Nom | Référence | Catégorie | Description | État | Localisation
États valides : disponible, emprunte, maintenance, retire

## Format Excel — Contacts
Colonnes : Nom | Prénom | Email | Téléphone | Type | Matricule | Filière
Types valides : etudiant, enseignant, personnel, externe

## Problèmes courants
- Erreur mysqlclient sur Windows → pip install PyMySQL + ajouter dans gestion_equipements/__init__.py :
  import pymysql; pymysql.install_as_MySQLdb()
- CSS ne charge pas → vérifier DEBUG=True dans settings.py
