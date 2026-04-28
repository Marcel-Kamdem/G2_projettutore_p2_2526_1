from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('authentification/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('toggle-status/<int:gest_id>/', views.toggle_status, name='toggle_status'),
    path('new-gestionnaire/', views.add_gestionnaire, name='creer_gestionnaire'),
    path('dashboard-admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard-gestionnaire/', views.dashboard_gestionnaire, name='dashboard_gestionnaire'),
    path('modifier-mot-de-passe/', views.modifier_mot_de_passe, name='modifier_mot_de_passe'),
    path('liste/', views.liste_emprunts, name='liste_emprunts'),

    path("emprunts/", views.liste_emprunts, name="liste_emprunts"),
    path("planification/", views.planification_emprunts, name="planification"),

    path("valider/<int:id>/", views.valider_emprunt, name="valider_emprunt"),
    path("refuser/<int:id>/", views.refuser_emprunt, name="refuser_emprunt"),
]