from django.db import models
from django.conf import settings 
from contacts.models import Contact
from equipements.models import Equipement 

class EmpruntForm(models.Model):
    EMPRUNT_STATE = [
        ("En attente", "En attente"), 
        ("Accepté", "Accepté"),
        ("Refusé", "Refusé"),
        ("En cours", "En cours"),
        ("Retourné", "Retourné"),
        ("Expiré", "Expiré"),
    ]

    gestionnaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="emprunts_crees"
    )
    beneficiaire = models.ForeignKey(Contact, on_delete=models.CASCADE)
    equipement = models.ForeignKey(Equipement, on_delete=models.CASCADE)
    object_dmd = models.CharField(max_length=150, verbose_name="Objet de la demande")
    date_empr = models.DateField(auto_now_add=True)
    date_retour_prevu = models.DateField()
    date_retour_effect = models.DateField(null=True, blank=True)
    etat = models.CharField(
        max_length=20, 
        choices=EMPRUNT_STATE, 
        default='En attente'
    )

    def __str__(self):
        return f"{self.equipement.nom} - {self.beneficiaire.nom} ({self.etat})"

    class Meta:
        verbose_name = "Emprunt"
        verbose_name_plural = "Emprunts"
