from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_contacts, name='liste_contacts'),
    path('creer/', views.creer_contact, name='creer_contact'),
    path('importer/', views.importer_contacts, name='importer_contacts'),
    path('<int:pk>/', views.detail_contact, name='detail_contact'),
    path('<int:pk>/modifier/', views.modifier_contact, name='modifier_contact'),
    path('<int:pk>/retirer/', views.retirer_contact, name='retirer_contact'),
]
