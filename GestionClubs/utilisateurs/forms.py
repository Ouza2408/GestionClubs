from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur

class InscriptionForm(UserCreationForm):
    role = forms.ChoiceField(choices=Utilisateur.ROLE_CHOICES)

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'role', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Désactive l'utilisateur par défaut
        user.statut = 'en_attente'
        if commit:
            user.save()
        return user

# Formulaire de connexion
class ConnexionForm(AuthenticationForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'password']
        labels = {
            'username': "Nom d'utilisateur",
            'password': "Mot de passe",
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'profile_picture', 'bio']