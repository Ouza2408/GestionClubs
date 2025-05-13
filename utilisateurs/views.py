from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm,ProfileForm
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
    

@login_required
def admin_dashboard(request):
    if request.user.role != 'gerant':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('accueil')
    return render(request, 'utilisateurs/admin_dashboard.html')


@login_required
def responsable_dashboard(request):
    if request.user.role != 'responsable':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('accueil')
    
    # Récupérer les clubs gérés par le responsable
    clubs = Club.objects.filter(responsable=request.user)
    
    # Récupérer les événements associés aux clubs du responsable
    evenements = Evenement.objects.filter(club__in=clubs).order_by('date')
    
    # Récupérer tous les membres des clubs du responsable
    membres = Utilisateur.objects.filter(clubs__in=clubs).distinct()
    
    return render(request, 'utilisateurs/responsable_dashboard.html', {
        'clubs': clubs,
        'evenements': evenements,
        'membres': membres,
    })


@login_required
def etudiant_dashboard(request):
    evenements = Evenement.objects.all().order_by('date')  # Récupère tous les événements
    user_clubs = request.user.clubs.all()
    clubs_disponibles = Club.objects.exclude(id__in=user_clubs.values_list('id', flat=True))
    return render(request, 'utilisateurs/etudiant_dashboard.html', {
        'evenements': evenements,
        'clubs_disponibles': clubs_disponibles,
    })

@login_required
def rejoindre_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.method == 'POST':
        if request.user in club.membres.all():
            messages.warning(request, f"Vous êtes déjà membre du club {club.nom}.")
        else:
            club.membres.add(request.user)
            messages.success(request, f"Vous avez rejoint le club {club.nom} avec succès !")
    return redirect('etudiant_dashboard')

@login_required
def s_inscrire_evenement(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    if request.method == 'POST':
        if request.user in evenement.participants.all():
            messages.warning(request, f"Vous êtes déjà inscrit à l'événement {evenement.titre}.")
        else:
            evenement.participants.add(request.user)
            messages.success(request, f"Vous vous êtes inscrit à l'événement {evenement.titre} avec succès !")
    return redirect('etudiant_dashboard')



@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'utilisateurs/profile.html', {'form': form})

@login_required
def mes_clubs(request):
    clubs = request.user.clubs.all()  # Récupère tous les clubs de l'utilisateur
    return render(request, 'utilisateurs/mes_clubs.html', {'clubs': clubs})

@login_required
def mes_evenements(request):
    evenements = request.user.evenements_participes.all()
    return render(request, 'utilisateurs/mes_evenements.html', {'evenements': evenements})

@login_required
def profil_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    return render(request, 'clubs/profil_club.html', {'club': club})