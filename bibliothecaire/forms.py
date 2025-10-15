from django import forms

from .models import Membre, Livre, CD, DVD


class CreationMembre(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ["nom"]

class AjouterMedia(forms.Form):
    TYPE_CHOICES = [
        ('livre', 'Livre'),
        ('cd', 'CD'),
        ('dvd', 'DVD'),
        ('jeu', 'Jeu de Plateau'),
    ]

    type_media = forms.ChoiceField(choices=TYPE_CHOICES, label="Type de média")
    titre = forms.CharField(max_length=100, label="Titre")
    createur = forms.CharField(
        max_length=100,
        label="Auteur / Artiste / Réalisateur / Créateur"
    )

class EmpruntMediaForm(forms.Form):
    # selectionner le membre
    membre = forms.ModelChoiceField(
        queryset=Membre.objects.all(),
        label="Sélectionnez le membre"
    )

    # Selectionner le média (cd, dvd ou livre)
    media = forms.ChoiceField(
        choices=[],
        label="Sélectionnez le média"
    )

    def __init__(self, *args, **kwargs):
        # Recuperer le type de média (livre, cd ou dvd) passé en parametre
        type_media = kwargs.pop('type_media', None)
        type_media = (type_media or "").lower()
        super().__init__(*args, **kwargs)

        # si on a le type de media, on remplit la liste de media disponibles
        if type_media == 'livre':
            # on récupère tous les livres dispo
            livres_disponibles = Livre.objects.filter(disponible=True)
            # creer liste tuples(id, titre) pour le formulaire
            self.fields['media'].choices = [(livre.id, livre.titre) for livre in livres_disponibles]

        elif type_media == 'cd':
            # on récupère tous les cd dispo
            cds_disponibles = CD.objects.filter(disponible=True)
            # creer liste tuples(id, titre) pour le formulaire
            self.fields['media'].choices = [(cd.id, cd.titre) for cd in cds_disponibles]

        elif type_media == 'dvd':
            # on récupère tous les dvd dispo
            dvds_disponibles = DVD.objects.filter(disponible=True)
            # creer liste tuples(id, titre) pour le formulaire
            self.fields['media'].choices = [(dvd.id, dvd.titre) for dvd in dvds_disponibles]