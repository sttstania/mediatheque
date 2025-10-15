from datetime import timedelta, date

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
        """
        Méthode pour emprunter ce média.
        Met à jour les champs `disponible`, `date_emprunt` et `emprunteur`.
        """
        if not self.disponible:
            raise Exception(f"Le média {self.titre} n'est pas disponible.")
        self.disponible = False
        self.date_emprunt = date.today()
        self.emprunteur = emprunteur
        self.save()

    def retourner(self):
        """
        Méthode pour retourner ce media.
        Remet à jour les champs pour savoir que le media est disponible.
        """
        self.disponible = True
        self.date_emprunt = None
        self.emprunteur = None
        self.save()

    def est_en_retard(self):
        """
        Vérifie si le media est en retar(+7j)
        True si en retard, False sinon
        """
        if self.date_emprunt:
            return (date.today() - self.date_emprunt) >= timedelta(days=7)
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
        raise Exception("Les jeux de plateau ne peuvent pas être empruntés")

#--------------------------------------------
#Modèle Membre
#--------------------------------------------
class Membre(models.Model):
    nom = models.CharField(max_length=100)
    nombre_emprunts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom

    def mettre_a_jour(self, nouveau_nom):
        self.nom = nouveau_nom
        self.save()

    def supprimer(self):
        self.delete()

# =============================================
# Modèle Emprunteur
# =============================================
class Emprunteur(models.Model):
    """
    Représente le statut d'emprunt d'un membre.
    Un membre a un seul Emprunteur, mais un Emprunteur peut avoir plusieurs médias empruntés.
    """
    membre = models.OneToOneField(Membre, on_delete=models.CASCADE)
    bloque = models.BooleanField(default=False) #true si emprunteur bloqué(retard)

    def __str__(self):
        return f'Emprunteur: {self.membre.nom}'


    @property
    def medias(self):
        """
        Propriété retournant la liste de tous les médias empruntés par cet emprunteur.
        Utilise `chain` pour concaténer les requêtes sans évaluer chaque QuerySet.
        """
        medias = []
        medias.extend(Livre.objects.filter(emprunteur=self))
        medias.extend(CD.objects.filter(emprunteur=self))
        medias.extend(DVD.objects.filter(emprunteur=self))
        return medias

    def verifier_retard(self):
        """Met à jour lz statut 'bloque' si l'emprunteur a un retard."""
        self.bloque = any(media.est_en_retard() for media in self.medias)
        self.save()
        return self.bloque

    def peut_emprunter(self):
        """Vérifie si l'emprunteur peut emprunter(non bloqué, <= 3médias, aucun retard)"""
        self.verifier_retard()
        return not self.bloque and len(self.medias) < 3

    def emprunter_media(self, media):
        """
        Permet à l'emprunteur d'emprunter un média, si les conditions sont remplies.
        Crée un enregistrement Emprunt et met à jour le média.
        """
        if not self.peut_emprunter():
            raise Exception(f"Le membre {self.membre.nom} ne peut pas emprunter")

        if isinstance(media, Livre):
            Emprunt.objects.create(emprunteur=self, livre=media)
        elif isinstance(media, CD):
            Emprunt.objects.create(emprunteur=self, cd=media)
        elif isinstance(media, DVD):
            Emprunt.objects.create(emprunteur=self, dvd=media)
        else:
            raise Exception("Type de média non empruntable")
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
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE, null=True, blank=True)
    cd = models.ForeignKey(CD, on_delete=models.CASCADE, null=True, blank=True)
    dvd = models.ForeignKey(DVD, on_delete=models.CASCADE, null=True, blank=True)
    date_emprunt = models.DateField(auto_now_add=True) # date automatique a la création
    date_retour = models.DateField(null=True, blank=True ) # Null tant que non retourné

    def retourner(self):
        """
        Marque cet emprunt en retourné et met a jour le média.
        Returns:
        """
        self.date_retour = date.today()
        self.save()
        if self.livre:
            self.livre.retourner()
        if self.cd:
            self.cd.retourner()
        if self.dvd:
            self.dvd.retourner()

