from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from applibs.data_parser import Parser
from applibs.response_status_code import *
from applibs.generator import create_verification_token
from applibs.custom_login import LoginUserToken, ObtainRefreshToken

from user.models import User

# Create your views here.

# parser = Parser()

@authentication_classes([])
class UserLoginView(APIView):
    """
    A view that returns a templated HTML representation of a given user.
    """
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, *args, **kwargs):
        data = {}
        data['title'] = 'Login'
        return Response(data, template_name='auth/login.html')


@authentication_classes([])
class UserVerificationView(APIView):

    def get(self, request, uuid, token):
        get_token_from_uuid = create_verification_token(uuid)

        if get_token_from_uuid == token:
            User.objects.active_user(uuid)
            return Response({'success_code': USER_ACCOUNT_ACTIVATED}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'error_code': ACCOUNT_ACTIVATION_TOKEN_INVALID}, status=status.HTTP_400_BAD_REQUEST)
