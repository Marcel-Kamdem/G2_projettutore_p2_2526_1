from django.urls import path
from . import views

app_name = 'statistiques'

urlpatterns = [
    # Tableau de bord principal
    path('', views.tableau_bord_statistiques, name='tableau_bord'),

    # APIs JSON pour graphiques Chart.js
    path('api/equipements-etat/',      views.api_graphique_equipements_etat,     name='api_eq_etat'),
    path('api/equipements-categorie/', views.api_graphique_equipements_categorie, name='api_eq_categorie'),
    path('api/emprunts-mois/',         views.api_graphique_emprunts_mois,         name='api_emprunts_mois'),
    path('api/contacts-type/',         views.api_graphique_contacts_type,         name='api_contacts_type'),

    # Filtrage avancé
    path('filtrage/equipements/', views.filtrage_avance_equipements, name='filtrage_equipements'),
    path('filtrage/emprunts/',    views.filtrage_avance_emprunts,    name='filtrage_emprunts'),
]
