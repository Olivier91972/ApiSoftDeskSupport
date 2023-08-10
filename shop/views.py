from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from shop.serializers import UserSignupSerializer, ProjectListSerializer, ProjectDetailSerializer, UserSerializer, IssueListSerializer, IssueDetailSerializer, CommentListSerializer
from shop.models import Project, Contributor, Issue, Comment
from shop.mixins import GetDetailSerializerClassMixin
from shop.permissions import ProjectPermission, IssuePermission, CommentPermission, ContributorViewsetPermission


User = get_user_model()


class SignupViewset(APIView):

    """
    Créer un utilisateur. Renvoie le code 201 si créé avec succès
    """

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectViewset(GetDetailSerializerClassMixin, ModelViewSet):

    """
    Project endpoint.
    Create: N'importe qui
    Get list / details: Contributeur ou auteur
    Update / delete: Auteur
    """

    permission_classes = (ProjectPermission,)

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        projects_ids = [contributor.project_id.id for contributor in Contributor.objects.filter(user_id=self.request.user).all()]
        return Project.objects.filter(id__in=projects_ids)

    def get_projects(self):
        projects = Project.object.all()
        return projects

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data["author_user_id"] = request.user.pk
        request.POST._mutable = False
        project = super(ProjectViewset, self).create(request, *args, **kwargs)
        contributor = Contributor.objects.create(
            user_id=request.user,
            project_id=Project.objects.filter(id=project.data['id']).first()
        )
        contributor.save()
        return Response(project.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data["author_user_id"] = request.user.pk
        request.POST._mutable = False
        return super(ProjectViewset, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(ProjectViewset, self).destroy(request, *args, **kwargs)


class UserContributorsViewset(ModelViewSet):

    """
    Projects contributor endpoint. Utilisé pour obtenir / ajouter / supprimer des contributeurs d'un projet donné.
    Get renvoie des objets utilisateur, nous devons donc mapper cet ensemble de vues au modèle utilisateur.
    Get list / details: Contributeur ou auteur
    Create / update / delete: Auteur
    """

    permission_classes = (ContributorViewsetPermission,)

    serializer_class = UserSerializer

    def get_queryset(self):
        cont_usr_ids = [contributor.user_id.id for contributor in Contributor.objects.filter(project_id=self.kwargs['projects_pk'])]
        return User.objects.filter(id__in=cont_usr_ids)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            user_to_add = User.objects.filter(email=request.data['email']).first()
            if user_to_add:
                contributor = Contributor.objects.create(
                    user_id=user_to_add,
                    project_id=Project.objects.filter(id=self.kwargs['projects_pk']).first()
                )
                contributor.save()
                return Response(status=status.HTTP_201_CREATED)
            return Response(data={'erreur': "L'utilisateur n'existe pas !"})
        except IntegrityError:
            return Response(data={'erreur': 'Utilisateur déjà ajouté !'})

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        user_to_delete = User.objects.filter(id=self.kwargs['pk']).first()
        if user_to_delete == request.user:
            return Response(data={'erreur': 'Vous ne pouvez pas vous supprimer !'})
        if user_to_delete:
            contributor = Contributor.objects.filter(user_id=self.kwargs['pk'], project_id=self.kwargs['projects_pk']).first()
            if contributor:
                contributor.delete()
                return Response()
            return Response(data={'erreur': 'Contributeur non affecté au projet !'})
        else:
            return Response(data={'erreur': "L'utilisateur n'existe pas !"})


class IssuesViewset(GetDetailSerializerClassMixin, ModelViewSet):

    """
    Issue endpoint. Utilisé pour obtenir / ajouter / supprimer des problèmes d'un projet donné.
    Get list / details, Create: Contributeur ou auteur du projet
    Update / delete: Auteur du problème
    """

    permission_classes = (IssuePermission,)

    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['projects_pk'])

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data["author_user_id"] = request.user.pk
        if not request.data['assignee_user_id']:
            request.data["assignee_user_id"] = request.user.pk
        request.data["project_id"] = self.kwargs['projects_pk']
        request.POST._mutable = False
        return super(IssuesViewset, self).create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data["author_user_id"] = request.user.pk
        if not request.data['assignee_user_id']:
            request.data["assignee_user_id"] = request.user.pk
        request.data["project_id"] = self.kwargs['projects_pk']
        request.POST._mutable = False
        return super(IssuesViewset, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(IssuesViewset, self).destroy(request, *args, **kwargs)


class CommentViewset(GetDetailSerializerClassMixin, ModelViewSet):

    """
    Issue endpoint. Utilisé pour obtenir / ajouter / supprimer des commentaires d'un problème donné d'un projet donné.
    Get list / details, Create: Contributeur ou auteur du projet
    Update / delete: Auteur du commentaire
    """

    permission_classes = (CommentPermission,)

    serializer_class = CommentListSerializer
    detail_serializer_class = CommentListSerializer

    def get_queryset(self):
        return Comment.objects.filter(issue_id=self.kwargs['issues_pk'])

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data['author_user_id'] = request.user.pk
        request.data['issue_id'] = self.kwargs['issues_pk']
        request.POST._mutable = False
        return super(CommentViewset, self).create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data['author_user_id'] = request.user.pk
        request.data['issue_id'] = self.kwargs['issues_pk']
        request.POST._mutable = False
        return super(CommentViewset, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super(CommentViewset, self).destroy(request, *args, **kwargs)
