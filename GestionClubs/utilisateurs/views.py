from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm


from django.shortcuts import render

def accueil(request):
    if request.user.is_authenticated:
        return redirect_role(request.user)  # Redirige selon le rôle si connecté
    return render(request, 'utilisateurs/accueil.html')  # Page d'accueil pour les non-connectés

def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie !")
            return redirect_role(user)  # Redirection selon le rôle
        else:
            messages.error(request, "Erreur dans le formulaire. Veuillez vérifier vos informations.")
    else:
        form = InscriptionForm()
    return render(request, 'utilisateurs/inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect_role(user)  # Redirection selon le rôle
        else:
            messages.error(request, "Identifiants incorrects. Veuillez réessayer.")
    else:
        form = ConnexionForm()
    return render(request, 'utilisateurs/connexion.html', {'form': form})

def deconnexion(request):
    logout(request)
    messages.success(request, "Déconnexion réussie !")
    return redirect('connexion')

def redirect_role(user):
    """Redirige l'utilisateur selon son rôle."""
    if user.role == 'admin':
        return redirect('admin_dashboard')  # À créer plus tard
    elif user.role == 'responsable':
        return redirect('responsable_dashboard')  # À créer plus tard
    else:  # étudiant
        return redirect('etudiant_dashboard')  # À créer plus tard
    

def admin_dashboard(request):
    return render(request, 'utilisateurs/admin_dashboard.html', {'user': request.user})

def responsable_dashboard(request):
    return render(request, 'utilisateurs/responsable_dashboard.html', {'user': request.user})

def etudiant_dashboard(request):
    return render(request, 'utilisateurs/etudiant_dashboard.html', {'user': request.user})