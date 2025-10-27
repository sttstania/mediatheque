from django.shortcuts import render
from bibliothecaire.models import Livre, CD, DVD, JeuDePlateau


def liste_media_membres(request):
    media_type = request.GET.get('type', 'tous')

    livres = Livre.objects.all() if media_type in ['tous', 'livre'] else []
    dvds = DVD.objects.all() if media_type in ['tous', 'dvd'] else []
    cds = CD.objects.all() if media_type in ['tous', 'cd'] else []
    jeux = JeuDePlateau.objects.all() if media_type in ['tous', 'jeu'] else []

    types = [
        {'type': 'tous', 'label': 'Tous'},
        {'type': 'livre', 'label': 'Livre'},
        {'type': 'dvd', 'label': 'DVD'},
        {'type': 'cd', 'label': 'CD'},
        {'type': 'jeu', 'label': 'Jeux de plateau'},
    ]

    return render(request, 'liste_media_membre.html', {
        'livres': livres,
        'dvds': dvds,
        'cds': cds,
        'jeux': jeux,
        'selected_type': media_type,
        'types': types,
    })