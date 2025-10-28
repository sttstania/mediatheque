import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from datetime import timedelta, date

from .models import Membre, Emprunt, Emprunteur, Livre, JeuDePlateau, CD, DVD


# ------------------
# test unitaires de base
# ---------------------

@pytest.mark.django_db
def test_membre_creation():
    """Un membre peut être créé correctement."""
    m = Membre.objects.create(nom="Leonard")
    assert m.nom == "Leonard"
    assert m.nombre_emprunts == 0

@pytest.mark.django_db
def test_emprunteur_creation():
    """Création d’un emprunteur à partir d’un membre."""
    membre = Membre.objects.create(nom="Bob")
    emprunteur = Emprunteur.objects.create(membre=membre)
    assert emprunteur.membre.nom == "Bob"
    assert emprunteur.bloque is False
    assert emprunteur.medias == []


# ------------------
# Tests des emprunts, retours
#-----------------

@pytest.mark.django_db
def test_emprunt_livre():
    """Emprunt d’un livre disponible."""
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
    """Retour d’un livre emprunté."""
    membre = Membre.objects.create(nom="Lina")
    emprunteur = Emprunteur.objects.create(membre=membre)
    livre = Livre.objects.create(titre="Livre2", auteur="Auteur2")

    emprunteur.emprunter_media(livre)

    #retour
    emprunteur.retourner_media(livre)
    livre.refresh_from_db()

    assert livre.disponible is True
    assert livre.emprunteur is None


# --------------------
# Règles métier
# -------------------

@pytest.mark.django_db
def test_emprunt_limit_et_retarde():
    """Un membre ne peut pas emprunter plus de 3 médias et est bloqué s’il a du retard."""
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

    # Bloqué à cause du retard
    with pytest.raises(Exception):
        emprunteur.emprunter_media(livre_extra)


@pytest.mark.django_db
def test_emprunt_duree_une_semaine():
    membre = Membre.objects.create(nom="Lucie")
    emprunteur = Emprunteur.objects.create(membre=membre)
    livre = Livre.objects.create(titre="Livre3", auteur="Auteur3")

    emprunteur.emprunter_media(livre)
    emprunt = Emprunt.objects.get(livre=livre)

    assert (date.today() - emprunt.date_emprunt) <= timedelta(days=7)


@pytest.mark.django_db
def test_jeu_de_plateau_non_empruntable():
    """Les jeux de plateau ne peuvent pas être empruntés."""
    jeu = JeuDePlateau.objects.create(titre="Monopoly", createur="hasbro")
    membre = Membre.objects.create(nom="Jean")
    emprunteur = Emprunteur.objects.create(membre=membre)

    with pytest.raises(Exception):
        jeu.emprunter(emprunteur)


# -------------------------------
# 4. TESTS DE VUES / INTERFACE WEB
# -------------------------------

@pytest.mark.django_db
def test_client_login_logout():
    """Un bibliothécaire peut se connecter et se déconnecter."""
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
    """Affichage de la liste des médias (accessible aux membres)."""
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

@pytest.mark.django_db
def test_liste_membres_view(client):
    """Affichage de la liste des membres par le bibliothécaire."""
    Membre.objects.create(nom="Albert")
    response = client.get(reverse('bibliothecaire:liste_membres'))

    assert response.status_code == 200
    assert "Albert" in response.content.decode()


@pytest.mark.django_db
def test_update_membre():
    """Mise à jour d’un membre."""
    membre = Membre.objects.create(nom="Melissa Dupont")
    membre.nom = "Melissa Dupont"
    membre.save()

    assert Membre.objects.get(id=membre.id).nom == "Melissa Dupont"


@pytest.mark.django_db
def test_ajouter_media():
    """Ajout d’un média dans la base (bibliothécaire)."""
    livre = Livre.objects.create(titre="Nouveau livre", auteur="AuteurX")

    assert Livre.objects.count() == 1


@pytest.mark.django_db
def test_creer_emprunt_media_disponible():
    """Création d’un emprunt pour un média disponible."""
    membre = Membre.objects.create(nom="Léo")
    emprunteur = Emprunteur.objects.create(membre=membre)
    livre = Livre.objects.create(titre="Livre test", auteur="Auteur test")

    emprunteur.emprunter_media(livre)
    livre.refresh_from_db()

    assert livre.disponible is False
    assert livre.emprunteur == emprunteur


@pytest.mark.django_db
def test_retour_media():
    """Retour d’un média par un emprunteur."""
    membre = Membre.objects.create(nom="Marie")
    emprunteur = Emprunteur.objects.create(membre=membre)
    livre = Livre.objects.create(titre="Livre test", auteur="Auteur test")

    emprunteur.emprunter_media(livre)
    emprunteur.retourner_media(livre)
    livre.refresh_from_db()

    assert livre.disponible is True
    assert livre.emprunteur is None