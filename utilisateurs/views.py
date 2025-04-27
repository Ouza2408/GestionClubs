from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm
from .models import Club, Evenement, Utilisateur
from datetime import datetime
from django.contrib.auth.decorators import login_required


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
@login_required
def etudiant_dashboard(request):
    # Liste des clubs
    clubs = Club.objects.all()
    # Liste des événements à venir
    evenements = Evenement.objects.filter(date__gte=datetime.now()).order_by('date')
    return render(request, 'utilisateurs/etudiant_dashboard.html', {
        'clubs': clubs,
        'evenements': evenements,
    })

@login_required
def rejoindre_club(request, club_id):
    if request.user.utilisateur.role != 'etudiant':
        messages.error(request, "Seuls les étudiants peuvent rejoindre un club.")
        return redirect('etudiant_dashboard')
    club = get_object_or_404(Club, id=club_id)
    utilisateur = request.user.utilisateur
    if utilisateur in club.membres.all():
        messages.warning(request, f"Vous êtes déjà membre du club {club.nom}.")
    else:
        club.membres.add(utilisateur)
        messages.success(request, f"Vous avez rejoint le club {club.nom} avec succès !")
    return redirect('etudiant_dashboard')

@login_required
def s_inscrire_evenement(request, evenement_id):
    if request.user.utilisateur.role != 'etudiant':
        messages.error(request, "Seuls les étudiants peuvent s'inscrire à un événement.")
        return redirect('etudiant_dashboard')
    evenement = get_object_or_404(Evenement, id=evenement_id)
    utilisateur = request.user.utilisateur
    if utilisateur in evenement.participants.all():
        messages.warning(request, f"Vous êtes déjà inscrit à l'événement {evenement.titre}.")
    else:
        evenement.participants.add(utilisateur)
        messages.success(request, f"Vous vous êtes inscrit à l'événement {evenement.titre} avec succès !")
    return redirect('etudiant_dashboard')

@login_required
def profil_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    return render(request, 'clubs/profil_club.html', {'club': club})

