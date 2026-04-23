from django.db import models


class Contact(models.Model):
    TYPE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('personnel', 'Personnel'),
        ('externe', 'Externe'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=20, blank=True)
    type_contact = models.CharField(max_length=20, choices=TYPE_CHOICES, default='etudiant')
    matricule = models.CharField(max_length=50, blank=True, unique=True)
    filiere = models.CharField(max_length=100, blank=True)
    adresse = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_actif = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        verbose_name = "Contact"
        ordering = ['nom', 'prenom']
