from rest_framework.permissions import BasePermission
from shop.models import Project, Contributor


def check_contributor(user, project):
    for contributor in Contributor.objects.filter(project_id=project.id):
        if user == contributor.user_id:
            return True
    return False


class ContributorViewsetPermission(BasePermission):

    """
    Les contributeurs peuvent répertorier d'autres contributeurs, lire des détails à leur sujet
    Les auteurs peuvent répertorier, lire, ajouter, mettre à jour ou supprimer un contributeur
    """

    message = "Vous n'avez pas la permission de faire cela."

    def has_permission(self, request, view):
        if not request.user and request.user.is_authenticated:
            return False

        if view.action in ['retrieve', 'list']:
            return check_contributor(request.user, Project.objects.filter(id=view.kwargs['projects_pk']).first())

        elif view.action in ['update', 'partial_update', 'create', 'destroy']:
            return request.user == Project.objects.filter(id=view.kwargs['projects_pk']).first().author_user_id


class ProjectPermission(BasePermission):

    """
    Tout le monde peut créer un projet.
    Les auteurs peuvent créer, lire, mettre à jour et supprimer un projet.
    Les contributeurs peuvent Lister leurs projets, Lire un projet
    """

    message = "Vous n'avez pas la permission de faire cela."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve', 'list']:
            return check_contributor(request.user, obj)
        elif view.action in ['update', 'partial_update', 'destroy']:
            return request.user == obj.author_user_id


class IssuePermission(BasePermission):

    """
    L'auteur du problème peut mettre à jour et supprimer ses problèmes.
    Les contributeurs du projet peuvent Lister tous les problèmes du projet, Lire le problème ou Créer un problème.
    """

    message = "Vous n'avez pas la permission de faire cela."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if view.action in ['retrieve', 'list', 'create']:
            return check_contributor(request.user, obj.project_id)
        elif view.action in ['update', 'partial_update', 'destroy']:
            return request.user == obj.author_user_id


class CommentPermission(BasePermission):

    """
    L'auteur du commentaire peut mettre à jour ou supprimer ses commentaires.
    Les contributeurs du projet peuvent Lister tous les commentaires d'un ticket, Lire un commentaire ou Créer un commentaire.
    """

    message = "Vous n'avez pas la permission de faire cela."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if view.action in ['retrieve', 'list', 'create']:
            return check_contributor(request.user, obj.issue_id.project_id)
        elif view.action in ['update', 'partial_update', 'destroy']:
            return request.user == obj.author_user_id