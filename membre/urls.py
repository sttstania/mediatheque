from django.urls import path


from bibliothecaire.views import liste_membres

membre = 'app_membre'

urlpatterns = [
    path('liste_membres/', liste_membres, name='liste_membres'),
]