from django.contrib import admin
from .models import Equipement, Categorie

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']
    search_fields = ['nom']

@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ['nom', 'reference', 'categorie', 'etat', 'localisation', 'est_actif']
    list_filter = ['etat', 'categorie', 'est_actif']
    search_fields = ['nom', 'reference']
