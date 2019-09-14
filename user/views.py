from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.core.mail import send_mail, EmailMessage, BadHeaderError

from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from applibs.data_parser import Parser
from applibs.response_status_code import *
from applibs.generator import create_verification_token
from applibs.custom_login import LoginUserToken, ObtainRefreshToken

from mysite import settings
from user.models import User
from user.serializer import UserSerializer, UserRegistrationSerializer

# Create your views here.

parser = Parser()


@authentication_classes([])
class UserSendMail(View):

    def get(self, request):
        subject = 'Test'
        message = 'Hello world! Sending email from django'
        from_email = 'hossainimam313@gmail.com'
        to_email = 'elegantrakib@gmail.com'

        if subject and message and from_email:
            try:
                send_mail(subject, message, from_email, [to_email])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return HttpResponse('Mail sent')
        else:
            # In reality we'd use a form class
            # to get proper validation errors.
            return HttpResponse('Make sure all fields are entered and valid.')


@authentication_classes([])
class UserView(APIView):

    def get(self, request):
        """
        :param request:
        :return: success or error message

        :Url /api/v1/user/get/

        NB: uuid, password, is_active, is_deleted are not necessary
        """
        query_result = User.objects.all_user()
        user_serializer = UserSerializer(query_result, many=True)
        users = user_serializer.data
        if users:
            return Response({"user_info": users, 'success_code': USER_PROFILE_FOUND}, status=status.HTTP_200_OK)

        return Response({'error_code': USER_PROFILE_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([])
class UserModifyView(APIView):

    def get(self, request, username):
        """
        :param request:
        :return: success or error message

        :Url /api/v1/user/edit/<slug:username>/

        NB: uuid, password, is_active, is_deleted are not necessary
        """
        user = User.objects.get_user_by_username(username)
        if user:
            return Response({"user_info": parser.user_profile(user), 'success_code': USER_PROFILE_FOUND}, status=status.HTTP_200_OK)

        return Response({'error_code': USER_PROFILE_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        """
        :param request:
        :return: success or error message

        :Url /api/v1/user/create/
        :body
        {
            "name": "Demo",
            "username": "demo123",
            "email": "demo123@example.com",
            "password": "123456",
            "confirm_password": "123456"
        }
        """

        # code for registration using serializer
        user_serializer = UserRegistrationSerializer(data=request.data)
        user_serializer.is_valid()
        user_serializer.validate(request.data)
        user = User.objects.create_user(user_serializer.data)
        if user:
            # TODO: sent email with token
            verification_token = create_verification_token(user.uuid)
            generate_url = '{}/api/v1/user/account/verification/{}/{}/'.format(settings.BASE_DIR, user.uuid, verification_token)
            messages.success(request, 'Signup completed.')
            return Response({'success_code': USER_ACCOUNT_CREATED}, status=status.HTTP_201_CREATED)

        return Response({'error_message': user_serializer.errors, 'error_code': USER_FIELD_REQUIRED}, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, username):

        # these three things use to see the form data
        # return Response(request.META)
        # return Response(request.data)
        # return Response(request.body)

        # update user info
        # if request.user.username != username:
        #     return Response({'error_code': USER_MISMATCH}, status=status.HTTP_400_BAD_REQUEST)

        message, status_code = User.objects.update_user(username, request.data)
        return Response(message, status=status_code)


    def delete(self, request, username):
        # delete user info
        # if request.user.username != username:
        #     return Response({'error_code': USER_MISMATCH}, status=status.HTTP_400_BAD_REQUEST)

        try:
            update = User.objects.remove_user(username=username)
            return Response({'success_code': USER_UPDATED}, status=status.HTTP_200_OK)
        except:
            return Response({'error_code': USER_PROFILE_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)
