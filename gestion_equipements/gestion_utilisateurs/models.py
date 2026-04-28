from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = [
        ("Admin", "Administrateur"),
        ("Gest", "Gestionnaire")
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="Gestionnaire")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name']


class Administrateur(Utilisateur):
    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Administrateur"


class Gestionnaire(Utilisateur):
    class Meta:
        verbose_name = "Gestionnaire"

class Emprunt(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("valide", "Validé"),
        ("refuse", "Refusé"),
    ]

    beneficiaire = models.CharField(max_length=100)
    equipement = models.CharField(max_length=100)
    motif = models.TextField()
    date_emprunt = models.DateField()
    date_retour = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")

    def __str__(self):
        return f"{self.beneficiaire} - {self.equipement}"