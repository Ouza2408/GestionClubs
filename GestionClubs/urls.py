"""
URL configuration for GestionClubs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from utilisateurs import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
   
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('responsable/dashboard/', views.responsable_dashboard, name='responsable_dashboard'),
    path('etudiant/dashboard/', views.etudiant_dashboard, name='etudiant_dashboard'), 
    path('clubs/rejoindre/<int:club_id>/', views.rejoindre_club, name='rejoindre_club'),
    path('evenements/inscription/<int:evenement_id>/', views.s_inscrire_evenement, name='s_inscrire_evenement'),
    path('clubs/profil/<int:club_id>/', views.profil_club, name='profil_club'),
    path('', include('utilisateurs.urls')),             
    path('', include('clubs.urls', namespace='clubs')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)