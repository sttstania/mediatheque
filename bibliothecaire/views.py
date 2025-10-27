import logging

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Membre, Livre, JeuDePlateau, CD, DVD, Emprunteur, Emprunt
from .forms import CreationMembre, AjouterMedia, EmpruntMediaForm


def accueil(request):
    return render(request, 'accueil.html')

logger = logging.getLogger('mediatheque')

def custom_logout(request):
    logout(request)
    return render(request, "logout.html")

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("bibliothecaire:accueil")
        else:
            return render(request, "login.html", {"error": "Identifiants incorrects"})
    return render(request, "login.html")


@login_required
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

@login_required
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

@login_required
def supprimer_membre(request, membre_id):
        membre = get_object_or_404(Membre, id=membre_id)
        if request.method == "POST":
            membre.delete()
            return redirect("bibliothecaire:liste_membres")
        return render(request, "supprimer_membre.html", {"membre": membre})



def liste_membres(request):
    membres = Membre.objects.all().order_by('nom')

    for m in membres:
        if hasattr(m, 'emprunteur'):
            emprunteur = m.emprunteur
            emprunteur.verifier_retard()

            m.nb_emprunts = len(emprunteur.medias)
            m.medias = []

            for media in emprunteur.medias:
                # On ajoute un attribut 'type_media' lisible pour le template
                if hasattr(media, "auteur"):
                    media.type_media = "Livre"
                elif hasattr(media, "artiste"):
                    media.type_media = "CD"
                elif hasattr(media, "realisateur"):
                    media.type_media = "DVD"
                else:
                    media.type_media = "Inconnu"

                m.medias.append(media)
        else:
            m.nb_emprunts = 0
            m.medias = []

    return render(request, 'liste_membres.html', {'membres': membres})


def liste_media(request):
    media_type = request.GET.get('type', 'tous')
    livres = Livre.objects.all().order_by('titre') if media_type in ['tous', 'livre'] else []
    cds = CD.objects.all().order_by('titre') if media_type in ['tous', 'cd'] else []
    dvds = DVD.objects.all().order_by('titre') if media_type in ['tous', 'dvd'] else []
    jeux = JeuDePlateau.objects.all().order_by('titre') if media_type in ['tous', 'jeu'] else []

    types = [
        {'type': 'tous', 'label': 'Tous'},
        {'type': 'livre', 'label': 'Livre'},
        {'type': 'cd', 'label': 'CDs'},
        {'type': 'dvd', 'label': 'DVDs'},
        {'type': 'jeu', 'label': 'Jeux de plateau'},
    ]
    return render(
        request,
        'liste_media.html',
        {
            'livres': livres,
            'cds': cds,
            'dvds': dvds,
            'jeux': jeux,
            'selected_type': media_type,
            'types' : types,
        },
    )


@login_required
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
            elif type_media == "cd":
                CD.objects.create(titre=titre, artiste=createur)
            elif type_media == "dvd":
                DVD.objects.create(titre=titre, realisateur=createur)
            elif type_media == "jeu":
                JeuDePlateau.objects.create(titre=titre, createur=createur)

            return redirect("bibliothecaire:liste_media")
    else:
        form = AjouterMedia()

    return render(request, "ajouter_media.html", {"form": form})

@login_required
def modifier_media(request, type_media, media_id):
    if type_media.lower() == 'livre':
        media = get_object_or_404(Livre, id=media_id)
        champ_createur = 'auteur'
    elif type_media.lower() == 'cd':
        media = get_object_or_404(CD, id=media_id)
        champ_createur = 'artiste'
    elif type_media.lower() == 'dvd':
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

@login_required
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

@login_required
def emprunter_media(request):
    # Récuperer le type de média et ID depuis l'URL
    type_media = request.GET.get('type_media')


    if request.method == "POST":
        form = EmpruntMediaForm(request.POST, type_media=type_media)
        if form.is_valid():
            membre = form.cleaned_data['membre']
            media_id = form.cleaned_data['media']

            # recupère ou crée l'emprunteur associé au membre
            emprunteur, _ = Emprunteur.objects.get_or_create(membre=membre)

            # Recuperer le media selectionné
            if type_media == "livre":
                media = get_object_or_404(Livre, id=media_id)
            elif type_media == "cd":
                media = get_object_or_404(CD, id=media_id)
            elif type_media == "dvd":
                media = get_object_or_404(DVD, id=media_id)
            else:
                raise ValueError("Type de média inconnu.")

            # tente d'emprunter média
            try:
                emprunteur.emprunter_media(media)
                return redirect("bibliothecaire:liste_media")
            except Exception as e:
                form.add_error(None, str(e)) # Si erreur, on l'affiche dans le formulaire

    else:
        form = EmpruntMediaForm(type_media=type_media)

    # Affiche le formulaire
    return render(request, "emprunter_media.html", {"form": form})

@login_required
def retourner_media(request, type_media, media_id):
    #Récuperer le bon média
    if type_media.lower() == 'livre':
        media = get_object_or_404(Livre, id=media_id)
    elif type_media.lower() == 'cd':
        media = get_object_or_404(CD, id=media_id)
    elif type_media.lower() == 'dvd':
        media = get_object_or_404(DVD, id=media_id)
    else:
        raise ValueError("Type de media inconnu.")

    # Vérifier s'il est bien emprunté
    if media.disponible:
        return render(request, "retourner_media.html", {
            "media": media,
            "message": "Ce média n'est pas actuellement emprunté."
        })

    # Si confirmation de retour

    if request.method == "POST":
        emprunt = Emprunt.objects.filter(
            emprunteur=media.emprunteur,
            date_retour__isnull=True
        ).filter(
            **{type_media.lower(): media}
        ).first()

        if emprunt:
            emprunt.retourner()

        media.retourner()

        return redirect("bibliothecaire:liste_media")

    return render(request, "retourner_media.html", {"media": media})
