from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('club/<int:club_id>/rejoindre/', views.rejoindre_club, name='rejoindre_club'),
    path('clubs/liste/', views.liste_clubs, name='liste_clubs'),
    path('clubs/creer/', views.creer_club, name='creer_club'),
    path('club/<int:club_id>/modifier/', views.modifier_club, name='modifier_club'),
    path('club/<int:club_id>/supprimer/', views.supprimer_club, name='supprimer_club'),
    path('clubs/profil/<int:club_id>/', views.profil_club, name='profil_club'),
    path('club/<int:club_id>/membres/', views.consulter_membres, name='consulter_membres'),
    path('club/<int:club_id>/membre/<int:membre_id>/accepter/', views.accepter_membre, name='accepter_membre'),
    path('club/<int:club_id>/membre/<int:membre_id>/rejeter-demande/', views.rejeter_membre_demande, name='rejeter_membre_demande'),
    path('club/<int:club_id>/membre/<int:membre_id>/rejeter/', views.rejeter_membre, name='rejeter_membre'),
    path('evenements/liste/', views.liste_evenements, name='liste_evenements'),
    path('evenements/creer/', views.creer_evenement, name='creer_evenement'),
    path('evenement/<int:evenement_id>/modifier/', views.modifier_evenement, name='modifier_evenement'),
    path('evenement/<int:evenement_id>/publier/', views.publier_evenement, name='publier_evenement'),
    path('evenement/<int:evenement_id>/participants/', views.consulter_participants, name='consulter_participants'),
    path('evenement/<int:evenement_id>/participant/<int:participant_id>/accepter/', views.accepter_participant, name='accepter_participant'),
    path('evenement/<int:evenement_id>/participant/<int:participant_id>/rejeter-demande/', views.rejeter_participant_demande, name='rejeter_participant_demande'),
   
]