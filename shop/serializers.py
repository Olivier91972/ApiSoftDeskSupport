from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer, ValidationError, SerializerMethodField
from rest_framework_simplejwt.tokens import RefreshToken
from shop.models import Project, Contributor, Issue, Comment


# Renvoie le modèle utilisateur actif dans ce projet.
User = get_user_model()


class UserSignupSerializer(ModelSerializer):

    tokens = SerializerMethodField()
    # birthdate = SerializerMethodField()
    # age = SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'tokens', 'age']  # ,'birthdate'

    # @property
    # def age(self):
    #     return timezone.now().year - self.birthdate.year
    #
    # def calculate_age(self, instance):
    #     request = self.context.get('request')
    #     user = request.user
    #     if user.is_authenticated() and user.is_staff:
    #         return datetime.datetime.now().year - instance.dob.year
    #     return 'Hidden'

    # def max_min_validator(self, min_value=int):
    #     if min_value > 120:
    #         raise ValidationError("L'age ne peut pas être au dela de 120 ans.")
    #     elif min_value <= 0:
    #         raise ValidationError("L'age ne peut pas être 5 ans ou moins")
    #     else:
    #         return min_value

    def validate_email(self, value: str, valage=int) -> str:  # age=int
        if User.objects.filter(email=value).exists() and User.objects.filter(age=valage) > 14:  # and User.objects.filter(age=value) > 15:
            raise ValidationError("L'utilisateur existe déjà")
        elif User.objects.filter(email=value).exists() and User.objects.filter(age=valage) < 15:  # and User.objects.filter(age=value) < 15:
            raise ValidationError("Vous n'avez pas l'age minimum requis")
        return value

    def validate_password(self, value: str) -> str:
        if value is not None:
            return make_password(value)
        raise ValidationError("Le mot de passe est vide")

    def get_tokens(self, user: User) -> dict:
        tokens = RefreshToken.for_user(user)
        data = {
            "refresh": str(tokens),
            "access": str(tokens.access_token)
        }
        return data


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'age']


class ContributorSerializer(ModelSerializer):

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'project_id']


class ProjectListSerializer(ModelSerializer):

    class Meta:
        model = Project
        fields = ['id', 'title', 'type', 'author_user_id']


class ProjectDetailSerializer(ModelSerializer):

    issues = SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author_user_id', 'issues']

    def get_issues(self, instance):
        queryset = Issue.objects.filter(project_id=instance.id)
        return IssueListSerializer(queryset, many=True).data


class IssueListSerializer(ModelSerializer):

    class Meta:
        model = Issue
        fields = ['id', 'created_time', 'title', 'priority', 'tag', 'status', 'project_id']


class IssueDetailSerializer(ModelSerializer):

    comments = SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'created_time', 'title', 'description', 'priority', 'tag', 'status', 'author_user_id', 'assignee_user_id', 'project_id', 'comments']

    def get_comments(self, instance):
        queryset = Comment.objects.filter(issue_id=instance.id)
        return CommentListSerializer(queryset, many=True).data


class CommentListSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'created_time', 'description', 'author_user_id', 'issue_id']


