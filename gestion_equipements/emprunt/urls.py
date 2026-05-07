from django.urls import path
from . import views

urlpatterns = [
    # Liste des emprunts
    path('liste/', views.liste_emprunts, name='liste_emprunts'),

    # Import Excel/CSV - décommenter quand le membre aura mergé son code
    # path('importer/', views.importer_emprunts_view, name='importer_emprunts'),

    # Modifier un emprunt (champs limités : date_empr + beneficiaire)
    path('modifier/<int:pk>/', views.modifier_emprunt, name='modifier_emprunt'),

    # Page admin : emprunts en attente de validation
    path('validation/', views.validation_admin, name='validation_admin'),

    # Admin valide un emprunt
    path('valider/<int:pk>/', views.valider_emprunt, name='valider_emprunt'),

    # Admin refuse un emprunt
    path('refuser/<int:pk>/', views.refuser_emprunt, name='refuser_emprunt'),
]