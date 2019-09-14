import graphene
from user.models import User
from graphene_django.types import DjangoObjectType

class UserType(DjangoObjectType):

    class Meta:
        model = User


class UserQuery(graphene.ObjectType):
    users = graphene.List(UserType, first=graphene.Int())

    def resolve_users(self, info, **kwargs):
    	return User.objects.all()


schema = graphene.Schema(query=UserQuery)
