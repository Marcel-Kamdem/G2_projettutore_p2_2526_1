from django.db import models
from contacts.models import Contact

# Create your models here.
class Emprunt(models.Model):

    EMPRUNT_STATE = [
        ("En cours", "En cours"),
        ("Planifié", "Planifié"),
        ("Validé", "Validé"),
        ("Retourné", "Retourné"),
        ("Expiré", "Expiré"),
        ("Annulé", "Annulé"),
    ]

    beneficiaire = models.ForeignKey(Contact, on_delete=models.CASCADE)
    object_dmd = models.CharField(max_length=50)
    date_empr = models.DateField(auto_now_add=True)
    date_retour_prevu = models.DateField()
    date_retour_effect = models.DateField(null=True, blank=True)
    etat = models.CharField(max_length=90, choices=EMPRUNT_STATE, default='En cours')
    # Un attribut equipements est disponible pour acceder a tout les equipements depuis cette classe Ex: Emprunt.equipements.all()


