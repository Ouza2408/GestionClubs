from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('responsable', 'Responsable de club'),
        ('admin', 'Administrateur'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')

    def __str__(self):
        return self.username
    
class Club(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='clubs_responsable')
    date_creation = models.DateTimeField(auto_now_add=True)
    membres = models.ManyToManyField(Utilisateur, related_name='clubs_membres', blank=True)

    def __str__(self):
        return self.nom

class Evenement(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='evenements')
    date = models.DateTimeField()
    lieu = models.CharField(max_length=100)
    participants = models.ManyToManyField(Utilisateur, related_name='evenements', blank=True)

    def __str__(self):
        return self.titre