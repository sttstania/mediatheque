from django.shortcuts import render, redirect

from bibliothecaire.models import CreationMembre, Membre, Livre, JeuDePlateau, CD, DVD


def creation_membre(request):
    if request.method == "POST":
        form = CreationMembre(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            Membre.objects.create(nom=nom)
            return redirect("liste_membre")
    else:
        form = CreationMembre()
    return render(request, "creation_membre.html", {"form": form})



def liste_membre(request):
    membre = Membre.objects.all()
    return render(request,'liste_membre.html',{'membre':membre})

def liste_media(request):
    livre = Livre.objects.all()
    cds = CD.objects.all()
    dvds = DVD.objects.all()
    jeux = JeuDePlateau.objects.all()
    return render(
        request,
        'liste_media.html',
        {'livre':livre, 'cds':CD,'dvds':DVD,'jeux':jeux},
    )
