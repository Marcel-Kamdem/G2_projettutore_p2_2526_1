# Dans emprunt/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('liste/', views.liste_emprunts, name='liste_emprunts'),
]
