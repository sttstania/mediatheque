from django.shortcuts import render
from bibliothecaire.models import Livre, CD, DVD, JeuDePlateau


def liste_media_membres(request):
    livres = Livre.objects.all()
    dvds = DVD.objects.all()
    cds = CD.objects.all()
    jeux = JeuDePlateau.objects.all()
    return render(request, 'membre/liste_media_membres.html', {'livres': livres, 'dvds': dvds, 'cds': cds, 'jeux': jeux})