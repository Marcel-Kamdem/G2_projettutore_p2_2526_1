from django.contrib import admin
from .models import Mouvement

@admin.register(Mouvement)
class MouvementAdmin(admin.ModelAdmin):
    list_display = ['equipement', 'type_operation', 'etat', 'date_operation', 'beneficiaire', 'gestionnaire']
    list_filter = ['type_operation', 'etat']
    search_fields = ['equipement__nom', 'beneficiaire__nom']