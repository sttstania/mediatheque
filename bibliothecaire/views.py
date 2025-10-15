from django.shortcuts import render, redirect, get_object_or_404

from .models import Membre, Livre, JeuDePlateau, CD, DVD, Media
from .forms import CreationMembre, AjouterMedia


def creation_membre(request):
    if request.method == "POST":
        form = CreationMembre(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            Membre.objects.create(nom=nom)
            return redirect("bibliothecaire:liste_membres")
    else:
        form = CreationMembre()
    return render(request, "creation_membre.html", {"form": form})

def modifier_membre(request, membre_id):
    membre = get_object_or_404(Membre, id=membre_id)
    if request.method == "POST":
        form = CreationMembre(request.POST, instance=membre)
        if form.is_valid():
            form.save()
            return redirect("bibliothecaire:liste_membres")
    else:
        form = CreationMembre(instance=membre)
    return render(request, "modifier_membre.html", {"form": form, "membre": membre})

def supprimer_membre(request, membre_id):
        membre = get_object_or_404(Membre, id=membre_id)
        if request.method == "POST":
            membre.delete()
            return redirect("bibliothecaire:liste_membres")
        return render(request, "supprimer_membre.html", {"membre": membre})

def liste_membres(request):
    membre = Membre.objects.all()
    return render(request,'liste_membres.html',{'membres':membre})

def liste_media(request):
    livres = Livre.objects.all()
    cds = CD.objects.all()
    dvds = DVD.objects.all()
    jeux = JeuDePlateau.objects.all()
    return render(
        request,
        'liste_media.html',
        {'livres': livres, 'cds': cds,'dvds': dvds,'jeux': jeux, 'show_nav': True},
    )

def liste_livre(request):
    livres = Livre.objects.all()
    return render(request, 'liste_livre.html', {'livres': livres, 'show_nav': True})

def liste_cd(request):
    cds = CD.objects.all()
    return render(request, 'liste_cd.html', {'cds': cds, 'show_nav': True})

def liste_dvd(request):
    dvds = DVD.objects.all()
    return render(request, 'liste_dvd.html', {'dvds': dvds, 'show_nav': True})

def liste_jeux(request):
    jeux = JeuDePlateau.objects.all()
    return render(request, 'liste_jeux.html', {'jeux': jeux, 'show_nav': True})

def ajouter_media(request):
    if request.method == "POST":
        form = AjouterMedia(request.POST)
        if form.is_valid():
            type_media = form.cleaned_data['type_media']
            titre = form.cleaned_data['titre']
            createur = form.cleaned_data['createur']

            # creation objet selon type média
            if type_media == "livre":
                Livre.objects.create(titre=titre, auteur=createur)
            elif type_media == "CD":
                CD.objects.create(titre=titre, artiste=createur)
            elif type_media == "DVD":
                DVD.objects.create(titre=titre, realisateur=createur)
            elif type_media == "jeu":
                JeuDePlateau.objects.create(titre=titre, createur=createur)

            return redirect("bibliothecaire:liste_media")
    else:
        form = AjouterMedia()

    return render(request, "ajouter_media.html", {"form": form})

def modifier_media(request, type_media, media_id):
    if type_media.lower() == 'livre':
        media = get_object_or_404(Livre, id=media_id)
        champ_createur = 'auteur'
    elif type_media.lower() == 'CD':
        media = get_object_or_404(CD, id=media_id)
        champ_createur = 'artiste'
    elif type_media.lower() == 'DVD':
        media = get_object_or_404(DVD, id=media_id)
        champ_createur = 'realisateur'

    elif type_media.lower() == 'jeu':
        media = get_object_or_404(JeuDePlateau, id=media_id)
        champ_createur = 'createur'
    else:
        raise ValueError("Type de média inconnu.")

    initial_data = {
        'titre': media.titre,
        'createur': getattr(media, champ_createur, ""),
        'type_media': type_media,
    }

    if request.method == "POST":
        form = AjouterMedia(request.POST)
        if form.is_valid():
            media.titre = form.cleaned_data['titre']
            setattr(media, champ_createur, form.cleaned_data['createur'])
            media.save()
            return redirect("bibliothecaire:liste_media")

    else:
        form = AjouterMedia(initial=initial_data)
    return render(request, "modifier_media.html", {"form": form, "media": media})

def supprimer_media(request, type_media, media_id):
    if type_media.lower() == 'livre':
        media = get_object_or_404(Livre, id=media_id)
    elif type_media.lower() == 'cd':
        media = get_object_or_404(CD, id=media_id)
    elif type_media.lower() == 'dvd':
        media = get_object_or_404(DVD, id=media_id)
    elif type_media.lower() == 'jeu':
        media = get_object_or_404(JeuDePlateau, id=media_id)
    else:
        raise ValueError("Type de média inconnu.")

    if request.method == "POST":
        media.delete()
        return redirect("bibliothecaire:liste_media")

    return render(request, "supprimer_media.html", {"media": media })
