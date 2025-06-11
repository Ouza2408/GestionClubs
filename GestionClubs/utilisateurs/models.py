from django.db import models
from django import forms
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
    

    
class ChangerRoleForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['role']
        widgets = {
            'role': forms.Select(choices=[
                ('etudiant', 'Étudiant'),
                ('responsable', 'Responsable'),
                ('admin', 'Administrateur'),
            ]),
        }

