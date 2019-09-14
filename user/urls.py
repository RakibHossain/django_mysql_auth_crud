from django.urls import path
from user import views
from .schema import schema
from graphene_django.views import GraphQLView

urlpatterns = [
	
	# graphql route
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema), name='getGQLUser'),

    # user routes
    path('get/', views.UserView.as_view(), name='getUser'),
    path('create/', views.UserModifyView.as_view(), name='createUser'),
    path('edit/<slug:username>/', views.UserModifyView.as_view(), name='editUser'),
    path('update/<slug:username>/', views.UserModifyView.as_view(), name='updateUser'),
    path('delete/<slug:username>/', views.UserModifyView.as_view(), name='deleteUser'),
    path('send/email/', views.UserSendMail.as_view(), name='userSendMail'),
]
