from datetime import date, timedelta

from django.contrib.auth.models import User
from django.db import models

# media
class Media(models.Model):
    titre = models.CharField(max_length=200)
    disponible = models.BooleanField(default=True)
    date_emprunt = models.DateField(null=True, blank=True)
    emprunteur = models.ForeignKey(
        'Emprunteur', on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        abstract = True

    def emprunter(self, emprunteur):
        """Permet à un emprunteur d'emprunter ce média"""
        if not self.disponible:
            raise Exception (f"Le média {self.titre} n'est pas disponible.")
        self.disponible = False
        self.date_emprunt = date.today()
        self.emprunteur = emprunteur
        self.save()

    def retourner(self):
        """Retourne le média et le rend à nouveau disponible"""
        self.disponible = True
        self.date_emprunt = None
        self.emprunteur = None
        self.save()

    def est_en_retard(self):
        '''Vérifie si le média est en retard (plus de 7 jours)'''
        if self.date_emprunt:
            return (date.today() - self.date_emprunt) > timedelta(days=7)
        return False

# Médias spécifique
class Livre(Media):
    auteur = models.CharField(max_length=200)

class CD(Media):
    artiste = models.CharField(max_length=200)

class DVD(Media):
    realisateur = models.CharField(max_length=200)

class JeuDePlateau(Media):
    createur = models.CharField(max_length=200)

# Emprenteur
class Emprunteur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bloque = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def medias(self):
        """Retourne la liste de tous les médias empruntés par cet utilisateur"""
        return (
            list(Livre.objects.filter(emprunteur=self))
            + list(CD.objects.filter(emprunteur=self))
            + list(DVD.objects.filter(emprunteur=self))
        )

    def emprunter_media(self, media):
        """Permet d'emprunter un média si l'utilisateur n'est pas bloqué et n'a pas plus que 3 emprunts."""
        if self.bloque:
            raise Exception("Cet utilisateur est bloqué et ne peut pas emprunter des médias.")
        elif isinstance(media, JeuDePlateau):
            raise Exception("Les jeux de plateau ne peuvent pas être empruntés.")
        elif len(self.medias) >= 3:
            raise Exception("Impossible d'emprunter : limite de 3 médias atteint.")
        else:
            media.emprunter(self)

    def retourner_media(self, media):
        """Retourne un média emprunté par l'utilisateur"""
        if media in self.medias:
            media.retourner()


