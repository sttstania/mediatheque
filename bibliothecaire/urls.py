from django.urls import path
from . import views

app_name = 'bibliothecaire'
urlpatterns = [
    path('liste_media/', views.liste_media, name='liste_media'),
    path('liste_membres/', views.liste_membres, name='liste_membres'),
    #path('liste_livre', views.liste_livre, name='liste_livre'),
    path('creation_membre/', views.creation_membre, name='creation_membre'),
]