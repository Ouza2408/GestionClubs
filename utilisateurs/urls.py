from django.contrib import admin
from django.urls import path
from utilisateurs import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.accueil, name='accueil'),  # Ajout de l'URL racine
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('responsable/dashboard/', views.responsable_dashboard, name='responsable_dashboard'),
    path('etudiant/dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'),
]