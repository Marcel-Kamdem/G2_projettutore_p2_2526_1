from django.db import models
from django.core.exceptions import ValidationError
from contacts.models import Contact


class Equipement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

    def est_disponible(self):
        return not self.emprunts.filter(
            etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
        ).exists()


class Emprunt(models.Model):

    EMPRUNT_STATE = [
        ("EN_COURS", "En cours"),
        ("PLANIFIE", "Planifié"),
        ("VALIDE", "Validé"),
        ("RETOURNE", "Retourné"),
        ("EXPIRE", "Expiré"),
        ("ANNULE", "Annulé"),
        ("REFUSE", "Refusé"),
    ]

    equipement = models.ForeignKey(
        'equipements.Equipement',
        on_delete=models.CASCADE,
        related_name="emprunts"
    )

    beneficiaire = models.ForeignKey(Contact, on_delete=models.CASCADE)
    object_dmd = models.CharField(max_length=50)
    date_empr = models.DateField(auto_now_add=True)
    date_retour_prevu = models.DateField()
    date_retour_effect = models.DateField(null=True, blank=True)

    etat = models.CharField(
        max_length=20,
        choices=EMPRUNT_STATE,
        default="EN_COURS"
    )

    def clean(self):
        if self.equipement and self.etat in ["EN_COURS", "PLANIFIE", "VALIDE"]:
            existe = Emprunt.objects.filter(
                equipement=self.equipement,
                etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
            ).exclude(pk=self.pk).exists()

            if existe:
                raise ValidationError("Cet équipement est déjà utilisé.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.equipement} - {self.beneficiaire} ({self.etat})"