from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Utilisateur

# Formulaire d'inscription
class InscriptionForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")
    role = forms.ChoiceField(
        choices=Utilisateur.ROLE_CHOICES,
        required=True,
        label="Rôle",
        help_text="Sélectionnez votre rôle dans l'application."
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'role', 'password1', 'password2']
        labels = {
            'username': "Nom d'utilisateur",
            'password1': "Mot de passe",
            'password2': "Confirmation du mot de passe",
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

# Formulaire de connexion
class ConnexionForm(AuthenticationForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'password']
        labels = {
            'username': "Nom d'utilisateur",
            'password': "Mot de passe",
        }