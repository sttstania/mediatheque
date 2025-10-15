from django.urls import path
from . import views

app_name = 'bibliothecaire'
urlpatterns = [
    # Page d’accueil du bibliothécaire : liste des membres
    path('', views.liste_membres, name='liste_membres'),
    # Gestion des membres
    path('creation_membre/', views.creation_membre, name='creation_membre'),
    path('<int:membre_id>/modifier/', views.modifier_membre, name='modifier_membre'),
    path('<int:membre_id>/supprimer/', views.supprimer_membre, name='supprimer_membre'),
    # Médias
    path('media/', views.liste_media, name='liste_media'),
    path('media/livres/', views.liste_livre, name='liste_livre'),
    path('media/cds/', views.liste_cd, name='liste_cd'),
    path('media/dvds/', views.liste_dvd, name='liste_dvd'),
    path('media/jeux/', views.liste_jeux, name='liste_jeux'),
    path('media/ajouter/', views.ajouter_media, name='ajouter_media'),
]