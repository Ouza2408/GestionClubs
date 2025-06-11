from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur
from clubs.models import MembreClub

admin.site.register(Utilisateur, UserAdmin)
admin.site.register(MembreClub)