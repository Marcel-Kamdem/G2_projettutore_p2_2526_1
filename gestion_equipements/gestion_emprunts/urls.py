from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_emprunts, name='liste_emprunts'),
    path('<int:pk>/modifier/', views.modifier_emprunt, name='modifier_emprunt'),
    path('planifies/', views.liste_emprunts_planifies, name='liste_emprunts_planifies'),
    path('<int:pk>/valider/', views.valider_emprunt, name='valider_emprunt'),
    path('<int:pk>/rejeter/', views.rejeter_emprunt, name='rejeter_emprunt'),
]
