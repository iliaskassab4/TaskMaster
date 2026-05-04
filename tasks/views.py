# On importe les outils nécessaires de Django
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required   # NOUVEAU
from django.utils import timezone
from .models import Tache
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

# ============================================================
# VUE 1 : Liste des tâches
# ============================================================
@login_required   # NOUVEAU : si pas connecté → redirige vers /login/
def liste_taches(request):

    # MODIFIÉ : on filtre seulement les tâches du user connecté
    # request.user = l'utilisateur actuellement connecté
    taches = Tache.objects.filter(responsable=request.user)

    # Recherche par titre
    recherche = request.GET.get('q', '')
    # request.GET.get('q', '') = récupère ?q=... dans l'URL
    # Si rien tapé → retourne '' (chaîne vide)
    if recherche:
        taches = taches.filter(titre__icontains=recherche)
        # icontains = "contient ce mot" sans tenir compte majuscules/minuscules

    # Filtre par statut
    # NOUVEAU : Filtre par date limite
    date_limite = request.GET.get('date_limite', '')
    if date_limite:
        taches = taches.filter(date_limite=date_limite)
        # Cherche les tâches dont la date limite = la date choisie

    aujourd_hui = timezone.now().date()

    return render(request, 'tasks/liste.html', {
        'taches': taches,
        'aujourd_hui': aujourd_hui,
        'recherche': recherche,
    })

# ============================================================
# VUE 2 : Créer une tâche
# ============================================================
@login_required   # NOUVEAU : protection
def creer_tache(request):

    if request.method == 'POST':
        # request.method == 'POST' : l'user a soumis le formulaire

        titre = request.POST['titre']
        description = request.POST.get('description', '')
        statut = request.POST.get('statut', 'todo')
        date_limite = request.POST.get('date_limite') or None
        # or None : si le champ date est vide → stocke NULL dans la BDD

        Tache.objects.create(
            titre=titre,
            description=description,
            statut=statut,
            date_limite=date_limite,
            responsable=request.user   # NOUVEAU : assigne automatiquement l'user connecté
        )
        return redirect('liste_taches')
        # redirect : après création → retourne à la liste

    # Si méthode GET (l'user ouvre juste la page) → affiche le formulaire vide
    return render(request, 'tasks/formulaire.html')

# ============================================================
# VUE 3 : Modifier une tâche
# ============================================================
@login_required   # NOUVEAU : protection
def modifier_tache(request, pk):
    # pk = l'identifiant de la tâche (vient de l'URL /modifier/5/)

    # MODIFIÉ : on vérifie que la tâche appartient bien à l'user connecté
    # Si quelqu'un essaie de modifier la tâche d'un autre → page 404
    tache = get_object_or_404(Tache, pk=pk, responsable=request.user)

    if request.method == 'POST':
        tache.titre = request.POST['titre']
        tache.description = request.POST.get('description', '')
        tache.statut = request.POST.get('statut', 'todo')
        tache.date_limite = request.POST.get('date_limite') or None
        tache.save()   # sauvegarde les modifications dans la BDD
        return redirect('liste_taches')

    # GET : affiche le formulaire avec les données actuelles de la tâche
    return render(request, 'tasks/formulaire.html', {'tache': tache})

# ============================================================
# VUE 4 : Supprimer une tâche
# ============================================================
@login_required   # NOUVEAU : protection
def supprimer_tache(request, pk):

    # MODIFIÉ : vérifie que la tâche appartient à l'user connecté
    tache = get_object_or_404(Tache, pk=pk, responsable=request.user)
    tache.delete()   # supprime de la BDD
    return redirect('liste_taches')
# ============================================================
# VUE 5 : Inscription d'un nouvel utilisateur
# ============================================================
def inscription(request):
    # Cette vue n'a PAS @login_required
    # Car un nouveau user n'est pas encore connecté !

    if request.method == 'POST':
        # UserCreationForm : formulaire déjà fait par Django
        # Il gère : username, password, confirmation password
        # Il vérifie automatiquement que les 2 mots de passe sont identiques
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # is_valid() : vérifie que tout est correct
            # (username pas déjà pris, password assez fort, etc.)
            form.save()  # crée l'utilisateur dans la BDD

            # Affiche un message de succès (s'affiche dans le template)
            messages.success(request, 'Compte créé avec succès ! Connectez-vous.')

            return redirect('login')  # redirige vers la page de connexion

        # Si le formulaire est invalide → on réaffiche avec les erreurs
    else:
        # Méthode GET : l'user ouvre juste la page → formulaire vide
        form = UserCreationForm() # type: ignore

    return render(request, 'tasks/inscription.html', {'form': form})