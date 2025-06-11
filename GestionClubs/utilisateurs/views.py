from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm,ProfileForm
from .models import  Utilisateur,ChangerRoleForm
from evenements.models import Evenement
from clubs.models import Club, MembreClub
from django.utils import timezone

from django.contrib.auth.decorators import login_required


from django.shortcuts import render

def accueil(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('utilisateurs:admin_dashboard')  # Ajout de l'espace de noms
        elif request.user.role == 'responsable':
            return redirect('utilisateurs:responsable_dashboard')
        else:
            return redirect('utilisateurs:etudiant_dashboard')
    return render(request, 'utilisateurs/accueil.html')

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
    return redirect('utilisateurs:connexion')

def redirect_role(user):
    """Redirige l'utilisateur selon son rôle."""
    if user.role == 'admin':
        return redirect('utilisateurs:admin_dashboard')  # À créer plus tard
    elif user.role == 'responsable':
        return redirect('utilisateurs:responsable_dashboard')  # À créer plus tard
    else:  # étudiant
        return redirect('utilisateurs:etudiant_dashboard')  # À créer plus tard
    

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('utilisateurs:accueil')
    
    # Statistiques
    total_clubs = Club.objects.count()
    total_utilisateurs = Utilisateur.objects.count()
    total_evenements = Evenement.objects.count()
    evenements_publies = Evenement.objects.filter(status='publie').count()
    
    # Clubs récents
    clubs_recents = Club.objects.all().order_by('-id')[:5]
    
    # Utilisateurs par rôle
    utilisateurs_etudiants = Utilisateur.objects.filter(role='etudiant').count()
    utilisateurs_responsables = Utilisateur.objects.filter(role='responsable').count()
    utilisateurs_admins = Utilisateur.objects.filter(role='admin').count()
    
    # Demandes d'adhésion en attente
    demandes_membres = MembreClub.objects.filter(club__demandes_membres__isnull=False)[:5]
    
    # Événements à venir
    evenements_a_venir = Evenement.objects.filter(
        status='publie',
        date_debut__gte=timezone.now()
    ).order_by('date_debut')[:5]
    
    context = {
        'total_clubs': total_clubs,
        'total_utilisateurs': total_utilisateurs,
        'total_evenements': total_evenements,
        'evenements_publies': evenements_publies,
        'clubs_recents': clubs_recents,
        'utilisateurs_etudiants': utilisateurs_etudiants,
        'utilisateurs_responsables': utilisateurs_responsables,
        'utilisateurs_admins': utilisateurs_admins,
        'demandes_membres': demandes_membres,
        'evenements_a_venir': evenements_a_venir,
    }
    return render(request, 'utilisateurs/admin_dashboard.html', context)


@login_required
def responsable_dashboard(request):
    if request.user.role != 'responsable':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('utilisateurs:accueil')
    
    # Récupérer les clubs gérés par le responsable
    clubs = request.user.clubs_responsables.all()
    
    # Récupérer les événements associés aux clubs du responsable
    evenements = Evenement.objects.filter(
        club__in=clubs,
        date_debut__gte=timezone.now()
    ).order_by('date_debut')
    
    # Récupérer tous les membres des clubs du responsable
    membres = Utilisateur.objects.filter(clubs_responsables__in=clubs).distinct()
    
    return render(request, 'utilisateurs/responsable_dashboard.html', {
        'clubs': clubs,
        'evenements': evenements,
        'membres': membres,
    })


@login_required
def etudiant_dashboard(request):
    if request.user.role != 'etudiant':
        messages.error(request, "Accès réservé aux étudiants.")
        return redirect('utilisateurs:accueil')
    
    user_clubs = request.user.clubs_membres.all()
    clubs_disponibles = Club.objects.exclude(id__in=user_clubs.values_list('id', flat=True))
    evenements = Evenement.objects.filter(
        status='publie',
        date_debut__gte=timezone.now()
    ).order_by('date_debut')
    context = {
        'clubs': user_clubs,
        'clubs_disponibles': clubs_disponibles,
        'evenements': evenements,
    }
    return render(request, 'utilisateurs/etudiant_dashboard.html', context)

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
def changer_role_utilisateur(request, utilisateur_id):
    if request.user.role != 'admin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accueil')
    
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    if request.method == 'POST':
        form = ChangerRoleForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le rôle de {utilisateur.username} a été modifié.")
            return redirect('utilisateurs:gerer_utilisateurs')
    else:
        form = ChangerRoleForm(instance=utilisateur)
    
    context = {
        'form': form,
        'utilisateur': utilisateur,
    }
    return render(request, 'utilisateurs/changer_role_utilisateur.html', context)

@login_required
def gerer_utilisateurs(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('utilisateurs:accueil')
    
    utilisateurs = Utilisateur.objects.all()
    context = {
        'utilisateurs': utilisateurs,
    }
    return render(request, 'utilisateurs/gerer_utilisateurs.html', context)