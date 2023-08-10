from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):

    # Désactiver le champ du nom d'utilisateur et activer la connexion par e-mail
    username = None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Rendre un nouveau membre actif et personnel par défaut, afin qu'il puisse effectuer des opérations CRUD
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)


class Project(models.Model):

    # Définition des types de projets
    BACKEND = 'BACKEND'
    FRONTEND = 'FRONTEND'
    IOS = 'IOS'
    ANDROID = 'ANDROID'
    TYPES_CHOICES = (
        (BACKEND, 'Back-end'),
        (FRONTEND, 'Front-end'),
        (IOS, 'iOS'),
        (ANDROID, 'Android')
    )

    title = models.CharField(max_length=155)
    description = models.CharField(max_length=5000)
    type = models.CharField(max_length=12, choices=TYPES_CHOICES)
    author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )


class Contributor(models.Model):

    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project_id = models.ForeignKey(to=Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('project_id', 'user_id')


class Issue(models.Model):

    # Définition des priorités
    LOW = 'FAIBLE'
    MEDIUM = 'MOYENNE'
    HIGH = 'HAUTE'
    PRIORITY_CHOICES = (
        (LOW, 'Faible'),
        (MEDIUM, 'Moyenne'),
        (HIGH, 'Haute')
    )

    # Définition des balises
    BUG = 'BOGUE'
    FEATURE = 'FONCTION'
    TASK = 'TACHE'
    TAGS_CHOICES = (
        (BUG, 'Bogue'),
        (FEATURE, 'Fonction'),
        (TASK, 'Tâche')
    )

    # Définition du statut
    TODO = 'A FAIRE'
    IN_PROGRESS = 'EN COURS'
    FINISHED = 'FINI'
    STATUS_CHOICES = (
        (TODO, 'A faire'),
        (IN_PROGRESS, 'En cours'),
        (FINISHED, 'Fini')
    )

    title = models.CharField(max_length=155)
    description = models.CharField(max_length=5000)
    created_time = models.DateTimeField(auto_now_add=True)

    priority = models.CharField(max_length=12, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=12, choices=TAGS_CHOICES)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES)

    author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issue_author')

    assignee_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=author_user_id,
        related_name='issue_assignee')

    project_id = models.ForeignKey(
        to=Project,
        on_delete=models.CASCADE,
        related_name='issues'
    )


class Comment(models.Model):
    description = models.CharField(max_length=5000)
    created_time = models.DateTimeField(auto_now_add=True)

    author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_author')

    issue_id = models.ForeignKey(
        to=Issue,
        on_delete=models.CASCADE,
        related_name='comments')
