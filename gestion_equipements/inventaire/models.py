from django.db import models
from django.conf import settings
from salles.models import Salle
from equipements.models import Equipement


class Inventaire(models.Model):
    """
    Session d'inventaire globale créée par l'administrateur.
    Un inventaire couvre une période donnée et regroupe
    les vérifications de toutes les salles.
    """

    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('cloture', 'Clôturé'),
    ]

    date_debut = models.DateField(verbose_name="Date de début")
    date_fin   = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    description = models.TextField(blank=True, verbose_name="Description / Contexte")

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_cours',
        verbose_name="Statut"
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='inventaires_crees',
        verbose_name="Créé par"
    )

    date_creation  = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventaire du {self.date_debut.strftime('%d/%m/%Y')} ({self.get_statut_display()})"

    @property
    def nb_salles_verifiees(self):
        return self.lignes.values('salle').distinct().count()

    @property
    def nb_equipements_verifies(self):
        return self.lignes.count()

    @property
    def nb_absents(self):
        return self.lignes.filter(statut='absent').count()

    @property
    def nb_endommages(self):
        return self.lignes.filter(statut='endommage').count()

    @property
    def nb_presents(self):
        return self.lignes.filter(statut='present').count()

    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
        ordering = ['-date_debut']


class LigneInventaire(models.Model):
    """
    Ligne de vérification d'un équipement dans une salle,
    dans le cadre d'un inventaire donné.
    """

    STATUT_CHOICES = [
        ('present',   'Présent'),
        ('absent',    'Absent'),
        ('endommage', 'Endommagé'),
    ]

    inventaire = models.ForeignKey(
        Inventaire,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name="Inventaire"
    )

    salle = models.ForeignKey(
        Salle,
        on_delete=models.CASCADE,
        related_name='lignes_inventaire',
        verbose_name="Salle"
    )

    equipement = models.ForeignKey(
        Equipement,
        on_delete=models.CASCADE,
        related_name='lignes_inventaire',
        verbose_name="Équipement"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='present',
        verbose_name="Statut constaté"
    )

    quantite_attendue  = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantité attendue"
    )
    quantite_constatee = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité constatée"
    )

    observations = models.TextField(
        blank=True,
        verbose_name="Observations"
    )

    verifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lignes_verifiees',
        verbose_name="Vérifié par"
    )

    date_verification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de vérification"
    )

    def __str__(self):
        return (
            f"{self.equipement.nom} — {self.salle.nom} "
            f"({self.get_statut_display()})"
        )

    @property
    def ecart(self):
        """Différence entre quantité attendue et constatée."""
        return self.quantite_constatee - self.quantite_attendue

    class Meta:
        verbose_name = "Ligne d'inventaire"
        verbose_name_plural = "Lignes d'inventaire"
        # Un équipement ne peut apparaître qu'une fois par salle par inventaire
        unique_together = [('inventaire', 'salle', 'equipement')]
        ordering = ['salle', 'equipement']