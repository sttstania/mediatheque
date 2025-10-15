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
        {'livres': livres, 'cds': cds,'dvds': dvds,'jeux': jeux},
    )

def liste_livre(request):
    livres = Livre.objects.all()
    return render(request, 'liste_livre.html', {'livres': livres})

def liste_cd(request):
    cds = CD.objects.all()
    return render(request, 'liste_cd.html', {'cds': cds})

def liste_dvd(request):
    dvds = DVD.objects.all()
    return render(request, 'liste_dvd.html', {'dvds': dvds})

def liste_jeux(request):
    jeux = JeuDePlateau.objects.all()
    return render(request, 'liste_jeu.html', {'jeux': jeux})

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