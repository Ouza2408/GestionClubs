from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm,ProfileForm
from .models import  Utilisateur,ChangerRoleForm
from evenements.models import Evenement,InscriptionEvenement
from clubs.models import Club, MembreClub
from django.utils import timezone
from django.db.models import Q

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

    # Statistics
    total_clubs = Club.objects.count()
    total_utilisateurs = Utilisateur.objects.count()
    total_evenements = Evenement.objects.count()
    clubs_en_attente = Club.objects.filter(status='en_attente').count()
    demandes_adhesion = sum(club.demandes_membres.count() for club in Club.objects.all())
    demandes_inscription = sum(evenement.demandes_inscription.count() for evenement in Evenement.objects.all())

    stats = {
        'total_clubs': total_clubs,
        'total_utilisateurs': total_utilisateurs,
        'total_evenements': total_evenements,
        'clubs_en_attente': clubs_en_attente,
        'demandes_adhesion': demandes_adhesion,
        'demandes_inscription': demandes_inscription,
    }

    # Clubs
    clubs_en_attente = Club.objects.filter(status='en_attente')
    clubs_recents = Club.objects.all().order_by('-date_creation')[:5]

    # Users by role
    utilisateurs_par_role = {
        'etudiants': Utilisateur.objects.filter(role='etudiant').count(),
        'responsables': Utilisateur.objects.filter(role='responsable').count(),
        'admins': Utilisateur.objects.filter(role='admin').count(),
    }

    # Upcoming events
    evenements_a_venir = Evenement.objects.filter(
        date_debut__gte=timezone.now()
    ).order_by('date_debut')

    # Pending requests
    demandes_adhesion = [
        {'user': user, 'club': club}
        for club in Club.objects.all()
        for user in club.demandes_membres.all()
    ]
    demandes_inscription = [
        {'user': user, 'evenement': evenement}
        for evenement in Evenement.objects.all()
        for user in evenement.demandes_inscription.all()
    ]

    context = {
        'stats': stats,
        'clubs_en_attente': clubs_en_attente,
        'clubs_recents': clubs_recents,
        'utilisateurs_par_role': utilisateurs_par_role,
        'evenements_a_venir': evenements_a_venir,
        'demandes_adhesion': demandes_adhesion,
        'demandes_inscription': demandes_inscription,
    }
    return render(request, 'utilisateurs/admin_dashboard.html', context)

@login_required
def responsable_dashboard(request):
    if request.user.role != 'responsable':
        messages.error(request, "Accès réservé aux responsables.")
        return redirect('utilisateurs:accueil')

    # Get clubs managed by the user
    clubs_valides = request.user.clubs_responsables.filter(status='valide')
    clubs_en_attente = request.user.clubs_responsables.filter(status='en_attente')

    # Get all events for the user's clubs
    evenements = Evenement.objects.filter(
        club__responsable=request.user
    ).order_by('date_debut')

    # Get pending membership requests
    demandes_adhésion = [
        {'user': user, 'club': club}
        for club in clubs_valides
        for user in club.demandes_membres.all()
    ]

    # Get pending event inscription requests
    demandes_inscription = [
        {'user': user, 'evenement': evenement}
        for evenement in evenements
        for user in evenement.demandes_inscription.all()
    ]

    context = {
        'clubs_valides': clubs_valides,
        'clubs_en_attente': clubs_en_attente,
        'evenements': evenements,
        'demandes_adhésion': demandes_adhésion,
        'demandes_inscription': demandes_inscription,
    }
    return render(request, 'utilisateurs/responsable_dashboard.html', context)


@login_required
def etudiant_dashboard(request):
    if request.user.role != 'etudiant':
        messages.error(request, "Accès réservé aux étudiants.")
        return redirect('utilisateurs:accueil')
    
    # Clubs où l'étudiant est membre accepté
    user_clubs = request.user.clubs_membres.all()
    
    # Demandes d'adhésion en attente
    demandes_en_attente = request.user.demandes_clubs.all()
    
    # Clubs disponibles (exclure ceux où il est déjà membre ou a une demande en attente)
    club_ids = list(user_clubs.values_list('id', flat=True)) + list(demandes_en_attente.values_list('id', flat=True))
    clubs_disponibles = Club.objects.exclude(id__in=club_ids)
    
    # Événements visibles (publiés et à venir)
    evenements = Evenement.objects.filter(
        status='publie',
        date_debut__gte=timezone.now()
    ).order_by('date_debut')
    
    # Inscriptions en attente aux événements
    inscriptions_attente = InscriptionEvenement.objects.filter(
        utilisateur=request.user,
        statut='en_attente'
    ).select_related('evenement')
    
    context = {
        'clubs': user_clubs,
        'demandes_en_attente': demandes_en_attente,
        'clubs_disponibles': clubs_disponibles,
        'evenements': evenements,
        'inscriptions_attente': inscriptions_attente,
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
def changer_role(request):
    if request.user.role != 'admin':
        messages.error(request, "Seuls les administrateurs peuvent modifier les rôles.")
        return redirect('utilisateurs:accueil')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            if utilisateur == request.user:
                messages.error(request, "Vous ne pouvez pas modifier votre propre rôle.")
            elif new_role in ['etudiant', 'responsable', 'admin']:
                utilisateur.role = new_role
                utilisateur.save()
                messages.success(request, f"Le rôle de {utilisateur.username} a été changé en {utilisateur.get_role_display()}.")
            else:
                messages.error(request, "Rôle invalide.")
        except Utilisateur.DoesNotExist:
            messages.error(request, "Utilisateur non trouvé.")
        return redirect('utilisateurs:changer_role')

    utilisateurs = Utilisateur.objects.all()
    return render(request, 'utilisateurs/changer_role.html', {'utilisateurs': utilisateurs})

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