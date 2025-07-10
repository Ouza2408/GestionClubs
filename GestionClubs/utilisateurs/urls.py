from django.contrib import admin
from django.urls import path
from utilisateurs import views
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    
    path('', views.accueil, name='accueil'),
    path('etudiant/dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'),
    path('responsable/dashboard/', views.responsable_dashboard, name='responsable_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('etudiant/mes-clubs/', views.mes_clubs, name='mes_clubs'),
    path('evenement/<int:evenement_id>/inscription/', views.s_inscrire_evenement, name='s_inscrire_evenement'),
    path('club/<int:club_id>/rejoindre/', views.rejoindre_club, name='rejoindre_club'),
    path('utilisateurs/gerer/', views.gerer_utilisateurs, name='gerer_utilisateurs'),
    path('change-role/', views.changer_role, name='changer_role'),
    path('valider-club/<int:club_id>/', views.valider_club, name='valider_club'),
    path('rejeter-demande/<int:club_id>/', views.rejeter_demande, name='rejeter_demande'),
    path('attente-validation/', views.attente_validation, name='attente_validation'),
    path('accepter-inscription/<int:user_id>/', views.accepter_inscription_utilisateur, name='accepter_inscription_utilisateur'),
    path('rejeter-inscription/<int:user_id>/', views.rejeter_inscription_utilisateur, name='rejeter_inscription_utilisateur'),

]