from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'type_contact', 'matricule', 'filiere', 'est_actif']
    list_filter = ['type_contact', 'est_actif']
    search_fields = ['nom', 'prenom', 'email', 'matricule']
