from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('authentification/', views.login_view, name='login'),
    path('deconnexion/',views.logout_view, name='logout'),
    path('toggle-status/<int:gest_id>/', views.toggle_status, name='toggle_status'),
    path('new-gestionnaire/', views.add_gestionnaire, name='creer_gestionnaire'),
    path('dashboard-admin/' ,views.dashboard_admin, name='dashboard_admin'),
    path('dashboard-gestionnaire/', views.dashboard_gestionnaire, name='dashboard_gestionnaire'),
]