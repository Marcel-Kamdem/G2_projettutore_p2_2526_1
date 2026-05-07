from django.db import models
from django.utils import timezone
from contacts.models import Contact


class Emprunt(models.Model):
    """
    Modèle principal pour la gestion des emprunts.
    Toute la logique métier est ici (règle POO du Sprint 3).
    """

    EMPRUNT_STATE = [
        ("Expiré",     "Expiré"),
        ("Annulé",     "Annulé"),
        ("En attente", "En attente"),
        ("Planifié",   "Planifié"),
        ("Validé",     "Validé"),
        ("En cours",   "En cours"),
        ("Retourné",   "Retourné"),
    ]

    EMPRUNT_TYPE = [
        ("simple",   "Emprunt simple"),
        ("planifie", "Emprunt planifié"),
    ]

    beneficiaire      = models.ForeignKey(Contact, on_delete=models.CASCADE, verbose_name="Bénéficiaire")
    object_dmd        = models.CharField(max_length=200, verbose_name="Objet de la demande")
    date_empr         = models.DateField(verbose_name="Date d'emprunt")
    date_retour_prevu = models.DateField(verbose_name="Date de retour prévue")
    date_retour_effect= models.DateField(null=True, blank=True, verbose_name="Date effective de retour")
    etat              = models.CharField(max_length=90, choices=EMPRUNT_STATE, default='En attente', verbose_name="État")
    type_emprunt      = models.CharField(max_length=20, choices=EMPRUNT_TYPE, default='planifie', verbose_name="Type")

    class Meta:
        verbose_name         = "Emprunt"
        verbose_name_plural  = "Emprunts"
        ordering             = ['-date_empr']

    def __str__(self):
        return f"Emprunt #{self.pk} – {self.beneficiaire} ({self.etat})"

    # ──────────────────────────────────────────────────
    # MÉTHODES POO ici
    # ──────────────────────────────────────────────────


    def refuser_emprunt(self):
        """Admin refuse → état passe à 'Annulé'. Retourne True si ok."""
        if self.etat in ("En attente", "Planifié"):
            self.etat = "Annulé"
            self.save()
            return True
        return False
    
    def valider_emprunt(self):
        """Admin valide → état passe à 'Validé'. Retourne True si ok."""
        if self.etat in ("En attente", "Planifié"):
            self.etat = "Validé"
            self.save()
            return True
        return False

    

    def est_expire(self):
        """True si la date prévue est dépassée et l'équipement pas encore rendu."""
        return (
            self.date_retour_effect is None
            and self.date_retour_prevu < timezone.now().date()
        )
    
    
    def marquer_retour(self):
        """Marque l'emprunt comme retourné avec la date du jour."""
        self.etat = "Retourné"
        self.date_retour_effect = timezone.now().date()
        self.save()

    def calculer_duree(self):
        """Nombre de jours entre emprunt et retour prévu."""
        return (self.date_retour_prevu - self.date_empr).days

    def changer_beneficiaire(self, nouveau_beneficiaire):
        """
        RG.04 – Modification autorisée : change le bénéficiaire.
        À appeler depuis la vue, pas directement depuis le formulaire.
        """
        self.beneficiaire = nouveau_beneficiaire
        self.save()

    def peut_etre_modifie(self):
        """Un emprunt ne peut être modifié que s'il n'est pas encore retourné/annulé."""
        return self.etat not in ("Retourné", "Annulé", "Expiré")
