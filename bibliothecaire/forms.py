from django import forms

from .models import Membre


class CreationMembre(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ["nom"]

class AjouterMedia(forms.Form):
    TYPE_CHOICES = [
        ('livre', 'Livre'),
        ('CD', 'CD'),
        ('DVD', 'DVD'),
        ('jeu', 'Jeu de Plateau'),
    ]

    type_media = forms.ChoiceField(choices=TYPE_CHOICES, label="Type de média")
    titre = forms.CharField(max_length=100, label="Titre")
    createur = forms.CharField(
        max_length=100,
        label="Auteur / Artiste / Réalisateur / Créateur"
    )