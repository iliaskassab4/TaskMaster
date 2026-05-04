from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Tache, Categorie

# ============================================================
# ADMIN DES CATÉGORIES
# ============================================================
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):

    # Colonnes visibles dans la liste
    list_display = ['nom', 'afficher_couleur', 'nombre_taches']

    # Barre de recherche
    search_fields = ['nom']

    # ----------------------------------------------------------
    # Méthode personnalisée : affiche un carré de couleur
    # ----------------------------------------------------------
    def afficher_couleur(self, obj):
        # format_html : génère du HTML en toute sécurité
        # On crée un petit carré coloré avec la couleur de la catégorie
        return format_html(
            '<div style="width:25px; height:25px; background-color:{}; '
            'border-radius:4px; border:1px solid #ccc;"></div>',
            obj.couleur  # ex: #3498db
        )
    afficher_couleur.short_description = 'Couleur'  # nom de la colonne

    # ----------------------------------------------------------
    # Méthode personnalisée : compte les tâches de cette catégorie
    # ----------------------------------------------------------
    def nombre_taches(self, obj):
        # obj = l'objet Categorie en cours
        # .tache_set.count() = compte les tâches liées à cette catégorie
        count = obj.tache_set.count()
        return f'{count} tâche(s)'
    nombre_taches.short_description = 'Nombre de tâches'


# ============================================================
# ADMIN DES TÂCHES
# ============================================================
@admin.register(Tache)
class TacheAdmin(admin.ModelAdmin):

    # ----------------------------------------------------------
    # COLONNES affichées dans la liste des tâches
    # ----------------------------------------------------------
    list_display = [
        'titre',
        'afficher_statut',    # statut avec badge coloré
        'responsable',        # qui a créé la tâche
        'categorie',
        'date_limite',
        'afficher_retard',    # indicateur en retard ou non
        'date_creation',
    ]

    # ----------------------------------------------------------
    # FILTRES sur le côté droit
    # ----------------------------------------------------------
    list_filter = [
        'statut',        # filtre par statut
        'categorie',     # filtre par catégorie
        'responsable',   # filtre par utilisateur
        'date_limite',   # filtre par date
    ]

    # ----------------------------------------------------------
    # BARRE DE RECHERCHE (cherche dans ces champs)
    # ----------------------------------------------------------
    search_fields = [
        'titre',
        'description',
        'responsable__username',  # cherche aussi par nom d'user
        # __ = accède au champ d'un autre modèle lié (ForeignKey)
    ]

    # ----------------------------------------------------------
    # ORDRE par défaut : les plus récentes d'abord
    # ----------------------------------------------------------
    ordering = ['-date_creation']
    # - devant = ordre décroissant (plus récent en premier)

    # ----------------------------------------------------------
    # ACTIONS GROUPÉES : sélectionner plusieurs tâches et faire une action
    # ----------------------------------------------------------
    actions = ['marquer_termine', 'marquer_en_cours', 'marquer_todo']

    def marquer_termine(self, request, queryset):
        # queryset = toutes les tâches sélectionnées
        queryset.update(statut='termine')
        # .update() = modifie toutes les tâches sélectionnées en une seule requête SQL
        self.message_user(request, f'{queryset.count()} tâche(s) marquée(s) comme terminée(s).')
    marquer_termine.short_description = '✔ Marquer comme Terminé'

    def marquer_en_cours(self, request, queryset):
        queryset.update(statut='en_cours')
        self.message_user(request, f'{queryset.count()} tâche(s) marquée(s) En cours.')
    marquer_en_cours.short_description = '🔄 Marquer comme En cours'

    def marquer_todo(self, request, queryset):
        queryset.update(statut='todo')
        self.message_user(request, f'{queryset.count()} tâche(s) marquée(s) À faire.')
    marquer_todo.short_description = '📋 Marquer comme À faire'

    # ----------------------------------------------------------
    # MÉTHODE : affiche le statut avec une couleur
    # ----------------------------------------------------------
    def afficher_statut(self, obj):
        # obj = la tâche en cours dans la boucle
        couleurs = {
            'todo':     ('#6c757d', 'À faire'),    # gris
            'en_cours': ('#ffc107', 'En cours'),   # jaune
            'termine':  ('#198754', 'Terminé'),    # vert
        }
        # .get(obj.statut, ...) : récupère la couleur selon le statut
        couleur, texte = couleurs.get(obj.statut, ('#000', obj.statut))

        return format_html(
            '<span style="background-color:{}; color:white; padding:3px 10px; '
            'border-radius:10px; font-size:12px; font-weight:bold;">{}</span>',
            couleur, texte
        )
    afficher_statut.short_description = 'Statut'

    # ----------------------------------------------------------
    # MÉTHODE : affiche si la tâche est en retard
    # ----------------------------------------------------------
    def afficher_retard(self, obj):
        aujourd_hui = timezone.now().date()

        if obj.statut == 'termine':
            # Tâche terminée → pas en retard
            return format_html('<span style="color:#198754;">✔</span>')

        if obj.date_limite and obj.date_limite < aujourd_hui:
            # Date dépassée → EN RETARD
            return format_html('<span style="color:#dc3545; font-weight:bold;">⚠ En retard</span>')

        if obj.date_limite:
            # Date pas encore dépassée → OK
            return format_html('<span style="color:#198754;">✔ OK</span>')

        # Pas de date limite définie
        return format_html('<span style="color:#aaa;">—</span>')

    afficher_retard.short_description = 'Délai'

    # ----------------------------------------------------------
    # FORMULAIRE DE DÉTAIL : organisation des champs
    # ----------------------------------------------------------
    fieldsets = (
        # Section 1 : infos principales
        ('📋 Informations principales', {
            'fields': ('titre', 'description', 'statut')
        }),
        # Section 2 : organisation
        ('👤 Organisation', {
            'fields': ('responsable', 'categorie', 'date_limite')
        }),
    )