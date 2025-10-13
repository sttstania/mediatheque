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
    # Liste des médias
    path('liste_media/', views.liste_media, name='liste_media'),
    path('liste_livre/', views.liste_livre, name='liste_livre'),
]