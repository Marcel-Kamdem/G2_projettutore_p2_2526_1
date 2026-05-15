# salles/models.py
from django.db import models

class Salle(models.Model):
    TYPE_CHOICES = [
        ('laboratoire', 'Laboratoire'),
        ('salle_cours', 'Salle de cours'),
        ('atelier', 'Atelier'),
        ('bureau', 'Bureau'),
        ('stock', 'Stock / Réserve'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100, unique=True)
    type_salle = models.CharField(max_length=20, choices=TYPE_CHOICES, default='autre')
    description = models.TextField(blank=True)
    capacite = models.PositiveIntegerField(null=True, blank=True)
    est_active = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_salle_display()})"

    @property
    def nombre_equipements(self):
        return self.equipements.count()

    class Meta:
        verbose_name = "Salle"
        ordering = ['nom']