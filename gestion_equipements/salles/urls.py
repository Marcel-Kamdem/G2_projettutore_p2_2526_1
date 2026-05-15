from django.urls import path
from . import views

app_name = 'salles'

urlpatterns = [
    path('', views.liste_salles, name='liste_salles'),
    path('creer/', views.creer_salle, name='creer_salle'),
    path('<int:pk>/', views.detail_salle, name='detail_salle'),
    path('<int:pk>/modifier/', views.modifier_salle, name='modifier_salle'),
    path('<int:pk>/supprimer/', views.supprimer_salle, name='supprimer_salle'),
]