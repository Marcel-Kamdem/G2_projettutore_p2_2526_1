from django.urls import path
from emprunt.views import liste_emprunts, importer_emprunts_view
from . import views

urlpatterns = [
    path('liste_emprunts', liste_emprunts, name='liste_emprunts'),
    path('importer/', importer_emprunts_view, name='importer_emprunts'),

    path('creer/', views.creer_emprunt, name='creer_emprunt'),
    path('<int:pk>/', views.detail_emprunt, name='detail_emprunt'),
    path('<int:pk>/modifier/', views.modifier_emprunt, name='modifier_emprunt'),
    path('<int:pk>/supprimer/', views.supprimer_emprunt, name='supprimer_emprunt'),

    path('planifications/', views.liste_planifications, name='liste_planifications'),

    path('<int:pk>/valider/', views.valider_planification, name='valider_planification'),
    path('<int:pk>/refuser/', views.refuser_planification, name='refuser_planification'),
    path('<int:pk>/en-cours/', views.passer_en_cours, name='passer_en_cours'),
]