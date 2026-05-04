from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# Modele utilisateur ~ motheer
class Utilisateur(AbstractUser):
    #Les attributs ID, et Mot de passes sonts geres automatiquement par django
    nom = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    ROLE_CHOICES = [('ADMIN','Administrateur'),('GEST','Gestionnaire')]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    #informations pour le login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nom']

    def __str__(self):
        return f"{self.nom} - {self.role} "



class Administrateur(Utilisateur):
    class Meta:
        verbose_name = "Administrateur"


class Gestionnaire(Utilisateur):
    class Meta:
        verbose_name = "Gestionnaire"
        verbose_name_plural = "Gestionnaires"