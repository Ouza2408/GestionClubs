from django.contrib import admin
from django.urls import path
from utilisateurs import views
from . import views

urlpatterns = [
    
    path('', views.accueil, name='accueil'),
    path('etudiant/dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'),
    path('responsable/dashboard/', views.responsable_dashboard, name='responsable_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('connexion/', views.connexion, name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('etudiant/mes-clubs/', views.mes_clubs, name='mes_clubs'),
    
   path('club/<int:club_id>/', views.profil_club, name='profil_club'),
    
    path('evenement/<int:evenement_id>/inscription/', views.s_inscrire_evenement, name='s_inscrire_evenement'),
    path('club/<int:club_id>/rejoindre/', views.rejoindre_club, name='rejoindre_club'),
]