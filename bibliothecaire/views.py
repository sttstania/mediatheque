from django.shortcuts import render, redirect

from bibliothecaire.models import CreationMembre, Membre, Livre, JeuDePlateau, CD, DVD




def creation_membre(request):
    if request.method == "POST":
        form = CreationMembre(request.POST)
        if form.is_valid():
            nom = form.cleaned_data['nom']
            Membre.objects.create(nom=nom)
            return redirect("liste_membres")
    else:
        form = CreationMembre()
    return render(request, "creation_membre.html", {"form": form})



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
