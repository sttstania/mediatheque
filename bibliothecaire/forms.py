from django import forms

from .models import Membre


class CreationMembre(forms.ModelForm):
    class Meta:
        model = Membre
        fields = ["nom"]
