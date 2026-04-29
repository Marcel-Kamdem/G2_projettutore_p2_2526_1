from django.urls import path
from emprunt.views import liste_emprunts, importer_emprunts_view

urlpatterns = [
    path('',         liste_emprunts,        name='liste_emprunts'),
    path('importer/', importer_emprunts_view, name='importer_emprunts'),
]