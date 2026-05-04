from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_taches, name='liste_taches'),          # page principale
    path('creer/', views.creer_tache, name='creer_tache'),      # créer une tâche
    path('modifier/<int:pk>/', views.modifier_tache, name='modifier_tache'),  # modifier
    path('supprimer/<int:pk>/', views.supprimer_tache, name='supprimer_tache'),# supprimer
    path('inscription/', views.inscription, name='inscription'),
]