from datetime import timedelta, date
from itertools import chain
from msilib.schema import Media

from django.contrib.auth.models import User
from django.db import models

#--------------------------------------------
#Modèle abstrait Media (base pour les médias)
#--------------------------------------------
class Media(models.Model):
    """
    Modèle abstrait représentant un média (livre, CD, DVD).
    Contient les champs et méthodes communs à tous les médias.
    """
    titre = models.CharField(max_length=100)
    disponible = models.BooleanField(default=True)
    date_emprunt = models.DateField(null=True, blank=True ) # Date d'emprunt (null si non emprunté)
    emprunteur = models.ForeignKey('Emprunteur', on_delete=models.SET_NULL, null=True, blank=True) # Emprunteur actuel


    class Meta:
        abstract = True

    def emprunter(self, emprunteur):
        '''
        Méthode pour emprunter ce média.
        Met à jour les champs `disponible`, `date_emprunt` et `emprunteur`.
        '''
        if not self.disponible:
            raise Exception(f"Le média {self.titre} n'est pas disponible.")
        self.disponible = False
        self.date_emprunt = date.today()
        self.emprunteur = emprunteur
        self.save()

    def retourner(self):
        '''
        Méthode pour retourner ce media.
        Remet à jour les champs pour savoir que le media est disponible.
        '''
        self.disponible = True
        self.date_emprunt = None
        self.emprunteur = None
        self.save()

    def est_en_retard(self):
        '''
        Vérifie si le media est en retar(+7j)
        True si en retard, False sinon
        '''
        if self.date_emprunt:
            return (date.today() - self.date_emprunt) > timedelta(days=7)
        return False


#--------------------------------------------
#Modeles concrets des Médias(héritent de Média)
#--------------------------------------------
class Livre(Media):
        auteur = models.CharField(max_length=100)

class CD(Media):
        artiste = models.CharField(max_length=100)

class DVD(Media):
        realisateur = models.CharField(max_length=100)

#--------------------------------------------
#Modele Jeu de plateau - non empruntable
#--------------------------------------------
class JeuDePlateau(models.Model):
    """
    Modèle pour les jeux de plateau, qui ne peuvent pas être empruntés.
    """
    titre = models.CharField(max_length=100)
    createur = models.CharField(max_length=100, blank=True, null=True)

    def emprunter(self, emprunteur):
        """
        Méthode pour interdire l'mprunt des jeux
        """
        raise Exception("Les jeux de plateau ne peuvent pas être empruntés")

#--------------------------------------------
#Modèle Membre
#--------------------------------------------
class Membre(models.Model):
    """
    Membre inscrit à la bibliotheque.
    Pas d'authentification.
    """
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_inscription = models.DateField(auto_now_add=True) # Date automatique à la création

    def __str__(self):
        return (f'{self.nom} {self.prenom}'
                f'({self.date_inscription})')

    class Meta:
        ordering = ['nom']  # Tri par nom dans l'admin et les requêtes

# =============================================
# Modèle Emprunteur (statut d'emprunt d'un membre)
# =============================================
class Emprunteur(models.Model):
    """
    Représente le statut d'emprunt d'un membre.
    Un membre a un seul Emprunteur, mais un Emprunteur peut avoir plusieurs médias empruntés.
    """
    membre = models.OneToOneField(Membre, on_delete=models.CASCADE)
    bloque = models.BooleanField(default=False) #true si emprunteur bloqué(retard)

    def __str__(self):
        return (f'Emprunteur: {self.membre.nom} {self.membre.prenom}')


    @property
    def medias(self):
        """
        Propriété retournant la liste de tous les médias empruntés par cet emprunteur.
        Utilise `chain` pour concaténer les requêtes sans évaluer chaque QuerySet.
        """
        return list(chain(
            Livre.objects.filter(emprunteur=self),
            CD.objects.filter(emprunteur=self),
            DVD.objects.filter(emprunteur=self),
        ))

    def a_un_retard(self):
        """
        Vérifie si l'emprenteur a au moins un média en retard
        """
        return any(media.est_en_retard() for media in self.medias)


    def verifier_retard(self):
        """
        Met à jour lz statut 'bloque' si l'emprunteur a un retard.
        Returns: True si bloqué, False sinon.
        """
        if self.a_un_retard():
            self.bloque = True
            self.save()
        return self.bloque

    def peut_emprunter(self):
        """
        Vérifie si l'emprunteur peut emprunter un nouveau média.
        - Non bloqué
        - Maximum 3 média empruntés
        - Aucun retard
        """
        self.verifier_retard() #mets à jours statut bloqué si retard
        return not self.bloque and len(self.medias) <= 3

    def emprunter_media(self, media):
        """
        Permet à l'emprunteur d'emprunter un média, si les conditions sont remplies.
        Crée un enregistrement Emprunt et met à jour le média.
        """
        if not self.peut_emprunter():
            raise Exception(f"Le membre {self.membre.nom} {self.membre.prenom} ne peut pas emprunter")
        Emprunt.objects.create(emprunteur=self, media=media) #crée un enregistrement d'emprunt
        media.emprunter(self) # met à jour média

    def retourner_media(self, media):
        """
        Permet à l'emprunteur de retourner un média.
        Vérifie que le média est bien emprunté par cet emprunteur avant de le retourner.
        """
        if media.emprunteur == self:
            media.retourner()
        else:
            raise Exception("Ce média n'est pas emprunter par ce membre")


# =============================================
# Modèle Emprunt (historique des emprunts)
# =============================================
class Emprunt(models.Model):
    """
    Represente un emprunt spécifique d'un média par un emprenteur.
    Permet de suivre l'historique et gérer les retards.
    """
    emprunteur = models.ForeignKey(Emprunteur, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    date_emprunt = models.DateField(auto_now_add=True) # date automatique a la création
    date_retour = models.DateField(null=True, blank=True ) # Null tant que non retourné

    def est_en_retard(self):
        """
        Vérifie si cet emprunt est en retard (emprunt >7jours).
        """
        if not self.date_retour and self.date_emprunt:
            return (date.today() - self.date_emprunt) > timedelta(days=7)
        return False

    def retourner(self):
        """
        Marque cet emprunt en retourné et met a jour le média.
        Returns:
        """
        self.date_retour = date.today()
        self.date_emprunt = None
        self.save()
        self.media.retourner()

