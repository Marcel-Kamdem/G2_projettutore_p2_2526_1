from django.db import models
from django.core.exceptions import ValidationError
from contacts.models import Contact
from django.conf import settings


class Mouvement(models.Model):

    ETAT_CHOICES = [
        ("EN_COURS", "En cours"),
        ("PLANIFIE", "Planifié"),
        ("VALIDE", "Validé"),
        ("RETOURNE", "Retourné"),
        ("EXPIRE", "Expiré"),
        ("ANNULE", "Annulé"),
        ("REFUSE", "Refusé"),
    ]

    TYPE_OPERATION_CHOICES = [
        ('entree', 'Entrée'),       # création / import d'équipement → stock initial
        ('emprunt', 'Emprunt'),     # prêt à un bénéficiaire (interne campus)
        ('sortie', 'Sortie'),       # envoi vers un autre campus (Eyang, etc.)
    ]

    DESTINATION_CHOICES = [
        ('eyang', 'Campus Eyang'),
        ('autre', 'Autre'),
    ]

    # --- Champ commun à toutes les opérations ---
    equipement = models.ForeignKey(
        'equipements.Equipement',
        on_delete=models.CASCADE,
        related_name="mouvements",
        verbose_name="Équipement"
    )

    type_operation = models.CharField(
        max_length=20,
        choices=TYPE_OPERATION_CHOICES,
        default='emprunt',
        verbose_name="Type d'opération"
    )

    date_operation = models.DateField(
        verbose_name="Date de l'opération"
    )

    gestionnaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_geres',
        verbose_name="Gestionnaire"
    )

    notes = models.TextField(blank=True, null=True, verbose_name="Notes")

    # --- Champs spécifiques aux emprunts ---
    beneficiaire = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Bénéficiaire"
    )
    objet_demande = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Objet de la demande"
    )
    date_retour_prevu = models.DateField(
        null=True, blank=True,
        verbose_name="Date retour prévue"
    )
    date_retour_effectif = models.DateField(
        null=True, blank=True,
        verbose_name="Date retour effective"
    )
    message_admin = models.TextField(
        blank=True, null=True,
        verbose_name="Message administrateur"
    )
    etat = models.CharField(
        max_length=20,
        choices=ETAT_CHOICES,
        default="EN_COURS",
        verbose_name="État"
    )

    # --- Champs spécifiques aux sorties ---
    destination = models.CharField(
        max_length=50,
        choices=DESTINATION_CHOICES,
        blank=True,
        null=True,
        verbose_name="Destination"
    )

    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def clean(self):
        # Un emprunt actif ne peut concerner qu'un équipement libre
        if self.type_operation == 'emprunt' and self.etat in ["EN_COURS", "PLANIFIE", "VALIDE"]:
            existe = Mouvement.objects.filter(
                equipement=self.equipement,
                type_operation='emprunt',
                etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
            ).exclude(pk=self.pk).exists()
            if existe:
                raise ValidationError("Cet équipement est déjà en cours d'emprunt.")

        # Bénéficiaire obligatoire pour un emprunt
        if self.type_operation == 'emprunt' and not self.beneficiaire:
            raise ValidationError("Un bénéficiaire est obligatoire pour un emprunt.")

        # Destination obligatoire pour une sortie
        if self.type_operation == 'sortie' and not self.destination:
            raise ValidationError("Une destination est obligatoire pour une sortie.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def est_emprunt_actif(self):
        return self.type_operation == 'emprunt' and self.etat in ["EN_COURS", "PLANIFIE", "VALIDE"]

    def __str__(self):
        if self.type_operation == 'emprunt':
            return f"Emprunt — {self.equipement} → {self.beneficiaire} ({self.etat})"
        elif self.type_operation == 'sortie':
            return f"Sortie — {self.equipement} → {self.get_destination_display()}"
        else:
            return f"Entrée — {self.equipement} ({self.date_operation})"

    class Meta:
        verbose_name = "Mouvement"
        verbose_name_plural = "Mouvements"
        ordering = ['-date_operation']