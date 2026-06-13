from django.urls import path
from . import views

urlpatterns = [
    # Liste principale (emprunts + sorties)
    path('', views.liste_mouvements, name='liste_mouvements'),

    # Rétro-compatibilité : l'ancienne URL 'liste_emprunts' redirige vers la nouvelle
    path('liste_emprunts', views.liste_mouvements, name='liste_emprunts'),

    # Import Excel (entrées en masse)
    path('importer/', views.importer_mouvements_view, name='importer_emprunts'),

    # CRUD
    path('creer/', views.creer_mouvement, name='creer_emprunt'),
    path('<int:pk>/', views.detail_mouvement, name='detail_emprunt'),
    path('<int:pk>/modifier/', views.modifier_mouvement, name='modifier_emprunt'),
    path('<int:pk>/supprimer/', views.supprimer_mouvement, name='supprimer_emprunt'),

    # Planifications
    path('planifications/', views.liste_planifications, name='liste_planifications'),
    path('<int:pk>/valider/', views.valider_planification, name='valider_planification'),
    path('<int:pk>/refuser/', views.refuser_planification, name='refuser_planification'),
    path('<int:pk>/en-cours/', views.passer_en_cours, name='passer_en_cours'),
]