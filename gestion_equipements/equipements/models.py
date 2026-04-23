from django.db import models
from emprunt.models import Emprunt

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie"
        ordering = ['nom']


class Equipement(models.Model):
    ETAT_CHOICES = [
        ('disponible', 'Disponible'),
        ('emprunte', 'Emprunté'),
        ('maintenance', 'En maintenance'),
        ('retire', 'Retiré'),
    ]

    nom = models.CharField(max_length=200)
    reference = models.CharField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='disponible')
    localisation = models.CharField(max_length=200, blank=True)
    date_acquisition = models.DateField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='equipements/', null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipements')
    emprunt = models.ForeignKey(Emprunt, on_delete=models.SET_NULL, blank=True, null=True, related_name="equipements")


    def __str__(self):
        return f"{self.nom} ({self.reference})"

    class Meta:
        verbose_name = "Équipement"
        ordering = ['nom']
