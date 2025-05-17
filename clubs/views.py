from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count 
from django.contrib.auth.decorators import login_required
from utilisateurs.models import Club, Utilisateur, Evenement
from django import forms

# Formulaire pour créer/modifier un club
class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['nom', 'description', 'logo', 'responsable']
        widgets = {
            'responsable': forms.Select(choices=[(u.id, u.username) for u in Utilisateur.objects.filter(role='responsable')]),
        }

# Page "Rejoindre un club" pour les étudiants
@login_required
def rejoindre_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    if request.user.role != 'etudiant':
        messages.error(request, "Seuls les étudiants peuvent rejoindre un club.")
        return redirect('etudiant_dashboard')
    
    if request.method == 'POST':
        if request.user in club.membres.all():
            messages.warning(request, f"Vous êtes déjà membre du club {club.nom}.")
        elif request.user in club.demandes_membres.all():
            messages.warning(request, f"Votre demande pour rejoindre le club {club.nom} est en attente de validation.")
        else:
            club.demandes_membres.add(request.user)
            messages.success(request, f"Votre demande pour rejoindre le club {club.nom} a été envoyée. Elle sera validée par un administrateur ou un responsable.")
    return redirect('etudiant_dashboard')

# Liste des clubs (pour les responsables et admins)
@login_required
def liste_clubs(request):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('accueil')
    
    if request.user.role == 'responsable':
        clubs = Club.objects.filter(responsable=request.user)
    else:  # rôle 'gerant'
        clubs = Club.objects.all()
    
    return render(request, 'clubs/liste_clubs.html', {'clubs': clubs})

@login_required
def profil_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    is_member = club.membres.filter(id=request.user.id).exists()
    is_leader = club.responsable == request.user or request.user.role == 'admin'
    #events = club.evenements_set.all()
    members = club.membres.all()  # Ensure this is included
    pending_requests = club.demandes_membres.all() if is_leader else []
    user_events = request.user.participants.all() if hasattr(request.user, 'participants') else []
    total_attendees = Evenement.objects.filter(club=club).aggregate(total=Count('participants'))['total'] or 0

    context = {
        'club': club,
        #'events': events,
        'members': members,
        'pending_requests': pending_requests,
        'is_member': is_member,
        'is_leader': is_leader,
        'user_events': user_events,
        'total_attendees': total_attendees,
    }
    return render(request, 'clubs/profil_club.html', context)

# Créer un club (pour les responsables et admins)
@login_required
def creer_club(request):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES)
        if form.is_valid():
            club = form.save()
            if request.user.role == 'responsable':
                club.responsable = request.user
                club.save()
            messages.success(request, f"Le club {club.nom} a été créé avec succès.")
            return redirect('clubs:liste_clubs')
    else:
        form = ClubForm()
    
    return render(request, 'clubs/creer_club.html', {'form': form})

# Modifier un club (pour les responsables et admins)
@login_required
def modifier_club(request, club_id):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    club = get_object_or_404(Club, id=club_id)
    if request.user.role == 'responsable' and club.responsable != request.user:
        messages.error(request, "Vous ne pouvez modifier que vos propres clubs.")
        return redirect('clubs:liste_clubs')
    
    if request.method == 'POST':
        form = ClubForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le club {club.nom} a été modifié avec succès.")
            return redirect('clubs:liste_clubs')
    else:
        form = ClubForm(instance=club)
    
    return render(request, 'clubs/modifier_club.html', {'form': form, 'club': club})

# Supprimer un club (pour les responsables et admins)
@login_required
def supprimer_club(request, club_id):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    club = get_object_or_404(Club, id=club_id)
    if request.user.role == 'responsable' and club.responsable != request.user:
        messages.error(request, "Vous ne pouvez supprimer que vos propres clubs.")
        return redirect('clubs:liste_clubs')
    
    if request.method == 'POST':
        club.delete()
        messages.success(request, "Le club a été supprimé avec succès.")
        return redirect('clubs:liste_clubs')
    
    return render(request, 'clubs/supprimer_club.html', {'club': club})

# Consulter les membres d'un club (pour les responsables et admins)
@login_required
def consulter_membres(request, club_id):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    club = get_object_or_404(Club, id=club_id)
    if request.user.role == 'responsable' and club.responsable != request.user:
        messages.error(request, "Vous ne pouvez consulter que les membres de vos propres clubs.")
        return redirect('liste_clubs')
    
    membres = club.membres.all()
    demandes_membres = club.demandes_membres.all()
    
    return render(request, 'clubs/consulter_membres.html', {
        'club': club,
        'membres': membres,
        'demandes_membres': demandes_membres,
    })

# Accepter un membre (pour les responsables et admins)
@login_required
def accepter_membre(request, club_id, membre_id):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    club = get_object_or_404(Club, id=club_id)
    membre = get_object_or_404(Utilisateur, id=membre_id)
    if request.user.role == 'responsable' and club.responsable != request.user:
        messages.error(request, "Vous ne pouvez gérer que les membres de vos propres clubs.")
        return redirect('liste_clubs')
    
    if request.method == 'POST':
        club.demandes_membres.remove(membre)
        club.membres.add(membre)
        messages.success(request, f"{membre.username} a été accepté dans le club {club.nom}.")
        return redirect('consulter_membres', club_id=club.id)
    
    return render(request, 'clubs/accepter_membre.html', {'club': club, 'membre': membre})

# Rejeter une demande de membre (pour les responsables et admins)
@login_required
def rejeter_membre_demande(request, club_id, membre_id):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    club = get_object_or_404(Club, id=club_id)
    membre = get_object_or_404(Utilisateur, id=membre_id)
    if request.user.role == 'responsable' and club.responsable != request.user:
        messages.error(request, "Vous ne pouvez gérer que les membres de vos propres clubs.")
        return redirect('liste_clubs')
    
    if request.method == 'POST':
        club.demandes_membres.remove(membre)
        messages.success(request, f"La demande de {membre.username} pour le club {club.nom} a été rejetée.")
        return redirect('consulter_membres', club_id=club.id)
    
    return render(request, 'clubs/rejeter_membre_demande.html', {'club': club, 'membre': membre})

# Rejeter un membre existant (pour les responsables et admins)
@login_required
def rejeter_membre(request, club_id, membre_id):
    if request.user.role not in ['responsable', 'admin']:
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    club = get_object_or_404(Club, id=club_id)
    membre = get_object_or_404(Utilisateur, id=membre_id)
    if request.user.role == 'responsable' and club.responsable != request.user:
        messages.error(request, "Vous ne pouvez gérer que les membres de vos propres clubs.")
        return redirect('liste_clubs')
    
    if request.method == 'POST':
        club.membres.remove(membre)
        messages.success(request, f"{membre.username} a été retiré du club {club.nom}.")
        return redirect('consulter_membres', club_id=club.id)
    
    return render(request, 'clubs/rejeter_membre.html', {'club': club, 'membre': membre})


# Liste des événements (pour l'admin)
@login_required
def liste_evenements(request):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('accueil')
    
    evenements = Evenement.objects.all()
    return render(request, 'clubs/liste_evenements.html', {'evenements': evenements})

# Créer un événement
@login_required
def creer_evenement(request):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "L'événement a été créé avec succès.")
            return redirect('liste_evenements')
    else:
        form = EvenementForm()
    
    return render(request, 'clubs/creer_evenement.html', {'form': form})

# Modifier un événement
@login_required
def modifier_evenement(request, evenement_id):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    evenement = get_object_or_404(Evenement, id=evenement_id)
    if request.method == 'POST':
        form = EvenementForm(request.POST, instance=evenement)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'événement {evenement.titre} a été modifié.")
            return redirect('liste_evenements')
    else:
        form = EvenementForm(instance=evenement)
    
    return render(request, 'clubs/modifier_evenement.html', {'form': form, 'evenement': evenement})

# Publier un événement
@login_required
def publier_evenement(request, evenement_id):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    evenement = get_object_or_404(Evenement, id=evenement_id)
    if request.method == 'POST':
        evenement.est_publie = True
        evenement.save()
        messages.success(request, f"L'événement {evenement.titre} a été publié.")
        return redirect('liste_evenements')
    
    return render(request, 'clubs/publier_evenement.html', {'evenement': evenement})

# Consulter les participants d'un événement
@login_required
def consulter_participants(request, evenement_id):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    evenement = get_object_or_404(Evenement, id=evenement_id)
    participants = evenement.participants.all()
    demandes_participants = evenement.demandes_participants.all()
    
    return render(request, 'clubs/consulter_participants.html', {
        'evenement': evenement,
        'participants': participants,
        'demandes_participants': demandes_participants,
    })

# Accepter un participant à un événement
@login_required
def accepter_participant(request, evenement_id, participant_id):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    evenement = get_object_or_404(Evenement, id=evenement_id)
    participant = get_object_or_404(Utilisateur, id=participant_id)
    
    if request.method == 'POST':
        evenement.demandes_participants.remove(participant)
        evenement.participants.add(participant)
        messages.success(request, f"{participant.username} a été accepté pour l'événement {evenement.titre}.")
        return redirect('consulter_participants', evenement_id=evenement.id)
    
    return render(request, 'clubs/accepter_participant.html', {'evenement': evenement, 'participant': participant})

# Rejeter une demande de participant
@login_required
def rejeter_participant_demande(request, evenement_id, participant_id):
    if request.user.role != 'admin':
        messages.error(request, "Vous n'avez pas accès à cette action.")
        return redirect('accueil')
    
    evenement = get_object_or_404(Evenement, id=evenement_id)
    participant = get_object_or_404(Utilisateur, id=participant_id)
    
    if request.method == 'POST':
        evenement.demandes_participants.remove(participant)
        messages.success(request, f"La demande de {participant.username} pour l'événement {evenement.titre} a été rejetée.")
        return redirect('consulter_participants', evenement_id=evenement.id)
    
    return render(request, 'clubs/rejeter_participant_demande.html', {'evenement': evenement, 'participant': participant})

# Formulaire pour créer/modifier un club
class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['nom', 'description', 'logo', 'responsable']
        widgets = {
            'responsable': forms.Select(choices=[(u.id, u.username) for u in Utilisateur.objects.filter(role='responsable')]),
        }
