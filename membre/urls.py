from django.urls import path



from membre.views import liste_media_membres

app_name = 'membre'

urlpatterns = [
    path('membres/', liste_media_membres, name='liste_media_membre'),
]