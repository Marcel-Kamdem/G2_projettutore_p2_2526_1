from django.contrib import admin
from .models import Beneficiaire, Equipement, Emprunt


@admin.register(Beneficiaire)
class BeneficiaireAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'prenom', 'email', 'type_beneficiaire', 'salle_classe')
    list_filter   = ('type_beneficiaire',)
    search_fields = ('nom', 'prenom', 'email')


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display  = ('nom', 'reference', 'statut')
    list_filter   = ('statut',)
    search_fields = ('nom', 'reference')


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display      = ('id', 'beneficiaire', 'type_emprunt', 'statut',
                         'date_emprunt', 'date_retour_prevue', 'valide_par')
    list_filter       = ('statut', 'type_emprunt')
    search_fields     = ('beneficiaire__nom', 'objet_demande')
    readonly_fields   = ('date_creation', 'date_validation', 'valide_par')
    filter_horizontal = ('equipements',)
