from urllib import response

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from datetime import timedelta, date

from .models import Membre, Emprunt, Emprunteur, Livre, JeuDePlateau, CD, DVD

@pytest.mark.django_db
def test_membre_creation():
    m = Membre.objects.create(nom="Leonard")
    assert m.nom == "Leonard"
    assert m.nombre_emprunts == 0

@pytest.mark.django_db
def test_emprunteur_creation():
    membre = Membre.objects.create(nom="Bob")
    emprunteur = Emprunteur.objects.create(membre=membre)
    assert emprunteur.membre.nom == "Bob"
    assert emprunteur.bloque is False
    assert emprunteur.medias == []

@pytest.mark.django_db
def test_emprunt_livre():
    membre = Membre.objects.create(nom="Lea")
    emprunteur = Emprunteur.objects.create(membre=membre)
    livre = Livre.objects.create(titre="Livre1", auteur="Auteur1")

    #avant emprunt
    assert livre.disponible is True

    #Emprunt
    emprunteur.emprunter_media(livre)

    livre.refresh_from_db()
    assert livre.disponible is False
    assert livre.emprunteur == emprunteur
    assert len(emprunteur.medias) == 1
    assert isinstance(emprunteur.medias[0], Livre)

@pytest.mark.django_db
def test_retour_livre():
    membre = Membre.objects.create(nom="Lina")
    emprunteur = Emprunteur.objects.create(membre=membre)
    livre = Livre.objects.create(titre="Livre2", auteur="Auteur2")
    emprunteur.emprunter_media(livre)

    #retour
    emprunteur.retourner_media(livre)
    livre.refresh_from_db()
    assert livre.disponible is True
    assert livre.emprunteur is None

@pytest.mark.django_db
def test_emprunt_limit_et_retarde():
    membre = Membre.objects.create(nom="Ella")
    emprunteur = Emprunteur.objects.create(membre=membre)

    #creer 3 livres empruntés
    for i in range(3):
        livre = Livre.objects.create(titre=f"Livre{i}", auteur="Auteur")
        emprunteur.emprunter_media(livre)

    #ne peut pas emprunter au 4eme media
    livre_extra = Livre.objects.create(titre="Extra", auteur="Auteur")
    with pytest.raises(Exception):
        emprunteur.emprunter_media(livre_extra)

    #Forcer un retard
    livre1 = emprunteur.medias[0]
    livre1.date_emprunt = date.today() - timedelta(days=10)
    livre1.save()

    assert emprunteur.verifier_retard() is True
    with pytest.raises(Exception):
        emprunteur.emprunter_media(livre_extra)

@pytest.mark.django_db
def test_jeu_de_plateau_non_empruntable():
    jeu = JeuDePlateau.objects.create(titre="Monopoly", createur="hasbro")
    membre = Membre.objects.create(nom="Jean")
    emprunteur = Emprunteur.objects.create(membre=membre)

    with pytest.raises(Exception):
        jeu.emprunter(emprunteur)


@pytest.mark.django_db
def test_client_login_logout():
    user = User.objects.create_user(username='testuser', password='12345')
    client = Client()

    #login correct
    reponse = client.post(reverse('bibliothecaire:login'), {'username': 'testuser', 'password': '12345'})
    assert reponse.status_code == 302 #redirection apres login

    #logout
    reponse = client.get(reverse('bibliothecaire:logout'))
    assert reponse.status_code == 200

@pytest.mark.django_db
def test_liste_media_view(client):
    Livre.objects.create(titre="Livre1", auteur="Auteur1")
    CD.objects.create(titre="CD1", artiste="Artiste1")
    DVD.objects.create(titre="DVD1", realisateur="Realisateur1")
    JeuDePlateau.objects.create(titre="JeuPlateau1", createur="Createur1")

    url = reverse('bibliothecaire:liste_media')
    reponse = client.get(url)

    assert reponse.status_code == 200
    content = reponse.content.decode()

    assert "Livre1" in content
    assert "CD1" in content
    assert "DVD1" in content
    assert "JeuPlateau1" in content
