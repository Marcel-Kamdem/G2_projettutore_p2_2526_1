from django.contrib import admin
from .models import Inventaire, LigneInventaire


class LigneInventaireInline(admin.TabularInline):
    model = LigneInventaire
    extra = 0
    fields = ['salle', 'equipement', 'statut', 'quantite_attendue', 'quantite_constatee', 'observations']


@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'statut', 'cree_par', 'nb_salles_verifiees', 'nb_equipements_verifies']
    list_filter = ['statut', 'date_debut']
    inlines = [LigneInventaireInline]


@admin.register(LigneInventaire)
class LigneInventaireAdmin(admin.ModelAdmin):
    list_display = ['equipement', 'salle', 'inventaire', 'statut', 'quantite_attendue', 'quantite_constatee']
    list_filter = ['statut', 'salle', 'inventaire']