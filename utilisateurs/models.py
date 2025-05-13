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
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    is_president = models.BooleanField(default=False)
    is_club_member = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
class Club(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='clubs_logos/', blank=True, null=True)
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='clubs_responsable')
    date_creation = models.DateTimeField(auto_now_add=True)
    membres = models.ManyToManyField(Utilisateur, related_name='clubs', blank=True)

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