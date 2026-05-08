from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_equipements, name='liste_equipements'),
    path('creer/', views.creer_equipement, name='creer_equipement'),
    path('importer/', views.importer_equipements, name='importer_equipements'),
    path('<int:pk>/', views.detail_equipement, name='detail_equipement'),
    path('<int:pk>/modifier/', views.modifier_equipement, name='modifier_equipement'),
    path('<int:pk>/retirer/', views.retirer_equipement, name='retirer_equipement'),
]
