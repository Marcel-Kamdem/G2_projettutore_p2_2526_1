from django.urls import path
from . import views

app_name = 'inventaire'

urlpatterns = [
    path('', views.liste_inventaires, name='liste_inventaires'),
    path('creer/', views.creer_inventaire, name='creer_inventaire'),
    path('<int:pk>/', views.detail_inventaire, name='detail_inventaire'),
    path('<int:pk>/cloturer/', views.cloturer_inventaire, name='cloturer_inventaire'),
    path('<int:pk>/supprimer/', views.supprimer_inventaire, name='supprimer_inventaire'),
    path('<int:inv_pk>/salle/<int:salle_pk>/', views.saisie_salle, name='saisie_salle'),
    path('<int:pk>/rapport/excel/', views.rapport_inventaire_excel, name='rapport_excel'),
    path('<int:pk>/rapport/pdf/', views.rapport_inventaire_pdf, name='rapport_pdf'),
    path('<int:pk>/salle/<int:salle_pk>/rapport/excel/', views.rapport_inventaire_excel, name='rapport_salle_excel'),
    path('<int:pk>/salle/<int:salle_pk>/rapport/pdf/', views.rapport_inventaire_pdf, name='rapport_salle_pdf'),
    path('<int:pk>/perte/excel/', views.rapport_perte_excel, name='rapport_perte_excel'),
    path('<int:pk>/perte/pdf/', views.rapport_perte_pdf, name='rapport_perte_pdf'),
]