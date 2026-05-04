from django.db import models
from django.utils import timezone
from gestion_utilisateur.models import Utilisateur


class Beneficiaire(models.Model):
    TYPE_CHOICES = [
        ('ETUDIANT',   'Étudiant'),
        ('ENSEIGNANT', 'Enseignant'),
        ('PERSONNEL',  'Personnel'),
    ]
    nom               = models.CharField(max_length=150)
    prenom            = models.CharField(max_length=150)
    email             = models.EmailField(unique=True)
    type_beneficiaire = models.CharField(max_length=20, choices=TYPE_CHOICES)
    salle_classe      = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.get_type_beneficiaire_display()})"

    class Meta:
        verbose_name        = "Bénéficiaire"
        verbose_name_plural = "Bénéficiaires"


class Equipement(models.Model):
    STATUT_CHOICES = [
        ('DISPONIBLE',    'Disponible'),
        ('INDISPONIBLE',  'Indisponible'),
        ('EN_REPARATION', 'En réparation'),
        ('DEFECTUEUX',    'Défectueux'),
    ]
    nom       = models.CharField(max_length=200)
    reference = models.CharField(max_length=100, unique=True)
    statut    = models.CharField(max_length=20, choices=STATUT_CHOICES, default='DISPONIBLE')

    def est_disponible(self):
        return self.statut == 'DISPONIBLE'

    def marquer_indisponible(self):
        self.statut = 'INDISPONIBLE'
        self.save(update_fields=['statut'])

    def marquer_en_reparation(self):
        self.statut = 'EN_REPARATION'
        self.save(update_fields=['statut'])

    def marquer_disponible(self):
        self.statut = 'DISPONIBLE'
        self.save(update_fields=['statut'])

    def __str__(self):
        return f"{self.nom} [{self.reference}] — {self.get_statut_display()}"

    class Meta:
        verbose_name        = "Équipement"
        verbose_name_plural = "Équipements"


class Emprunt(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDE',     'Validé'),
        ('EN_COURS',   'En cours'),
        ('RETOURNE',   'Retourné'),
        ('EXPIRE',     'Expiré'),
        ('ANNULE',     'Annulé'),
    ]
    TYPE_CHOICES = [
        ('SIMPLE',   'Emprunt simple'),
        ('PLANIFIE', 'Emprunt planifié'),
    ]

    beneficiaire          = models.ForeignKey(Beneficiaire, on_delete=models.PROTECT, related_name='emprunts')
    objet_demande         = models.CharField(max_length=255)
    date_emprunt          = models.DateField()
    date_retour_prevue    = models.DateField()
    date_retour_effective = models.DateField(null=True, blank=True)
    equipements           = models.ManyToManyField(Equipement, related_name='emprunts')
    statut                = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    type_emprunt          = models.CharField(max_length=10, choices=TYPE_CHOICES, default='SIMPLE')
    cree_par              = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='emprunts_crees')
    valide_par            = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='emprunts_valides')
    date_validation       = models.DateTimeField(null=True, blank=True)
    date_creation         = models.DateTimeField(auto_now_add=True)

    # ── Méthodes POO ──────────────────────────────────────────────────────────

    def valider_emprunt(self, admin_user):
        """RG.03 — Valide un emprunt planifié. Réservé à l'admin."""
        if self.type_emprunt != 'PLANIFIE':
            raise ValueError("Seuls les emprunts planifiés nécessitent une validation.")
        if self.statut != 'EN_ATTENTE':
            raise ValueError(f"Impossible de valider : statut actuel '{self.get_statut_display()}'.")
        self.statut          = 'VALIDE'
        self.valide_par      = admin_user
        self.date_validation = timezone.now()
        self.save(update_fields=['statut', 'valide_par', 'date_validation'])
        for eq in self.equipements.all():
            eq.marquer_indisponible()

    def rejeter_emprunt(self):
        """Annule un emprunt planifié en attente."""
        if self.statut != 'EN_ATTENTE':
            raise ValueError("Seuls les emprunts en attente peuvent être rejetés.")
        self.statut = 'ANNULE'
        self.save(update_fields=['statut'])

    def marquer_retour(self):
        """Enregistre le retour effectif et libère les équipements."""
        self.date_retour_effective = timezone.now().date()
        self.statut = 'RETOURNE'
        self.save(update_fields=['statut', 'date_retour_effective'])
        for eq in self.equipements.all():
            eq.marquer_disponible()

    def est_expire(self):
        """True si la date de retour prévue est dépassée et l'emprunt non clôturé."""
        return (
            self.date_retour_effective is None
            and self.date_retour_prevue < timezone.now().date()
            and self.statut not in ('RETOURNE', 'ANNULE', 'EXPIRE')
        )

    def calculer_duree(self):
        """Durée en jours."""
        fin = self.date_retour_effective or timezone.now().date()
        return (fin - self.date_emprunt).days

    def changer_beneficiaire(self, nouveau_beneficiaire):
        """RG.04 — Seul le bénéficiaire peut être changé après création."""
        self.beneficiaire = nouveau_beneficiaire
        self.save(update_fields=['beneficiaire'])

    def __str__(self):
        return f"Emprunt #{self.pk} — {self.beneficiaire} [{self.get_statut_display()}]"

    class Meta:
        verbose_name        = "Emprunt"
        verbose_name_plural = "Emprunts"
        ordering            = ['-date_creation']
