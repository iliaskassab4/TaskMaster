from django.db import models
from django.contrib.auth.models import User  


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    couleur = models.CharField(max_length=7, default='#3498db')  

    def __str__(self):
        return self.nom


class Tache(models.Model):
    
    
    STATUT_CHOICES = [
        ('todo', 'À faire'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]
    
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_limite = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='todo')
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre