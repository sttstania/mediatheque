from django.shortcuts import render, redirect, get_object_or_404

from .models import Membre, Livre, JeuDePlateau, CD, DVD
from .forms import CreationMembre



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

def supprimer_membre(request):
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