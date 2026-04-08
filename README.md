# Gestion d'Équipement - Dashboard

Ce projet est une application Django permettant de gérer des gestionnaires. Il utilise du JavaScript (Fetch API) pour mettre à jour les statuts en temps réel sans recharger la page.

## Installation rapide

1. **Cloner le projet**
   ```bash
   git clone https://github.comhttps://github.com/Marcel-Kamdem/G2_projettutore_p2_2526_1
   cd G2_projettutore_p2_2526_1

2. **Installer les dépendances(Activez votre environnement virtuel au préalable)**
    ```bash
    bashpip install -r requirements.txt

3. **Préparer la base de données**
    ```bash
    python manage.py migrate

4. **Créer un accès administrateur**
    ```bash
    python manage.py createsuperuser

5. **Lancer l'application**
    ```bash
    python manage.py runserver