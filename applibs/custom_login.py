import jwt
import json
from calendar import timegm
from datetime import datetime, timedelta

from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.http import HttpResponseBadRequest

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

# JWT modules call here
from rest_framework_jwt.authentication import jwt_decode_handler, jwt_get_username_from_payload
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken, JSONWebTokenAPIView
from rest_framework_jwt.views import jwt_response_payload_handler

# get user validation and role
from user.models import User
from user.serializer import UserSerializer
from .decorators import check_user
from applibs.response_status_code import *

token_decode = api_settings.JWT_DECODE_HANDLER
payload_handler = api_settings.JWT_PAYLOAD_HANDLER
encode_handler = api_settings.JWT_ENCODE_HANDLER

'''
#---------------------------------------------------------------------------------------#
|                                                                                       |
|                                                                                       |
|           Get User Information for Both User and Vendor From Token             |
|                                                                                       |
|                                                                                       |
#---------------------------------------------------------------------------------------#
'''


class GetUserInfo:

    def _check_payload(self, token: str) -> str:
        """
        :rtype: object
        """
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            msg = EXPIRED_SIGNATURE
            raise ValidationError(msg)
        except jwt.DecodeError:
            msg = SIGNATURE_DECODE_ERROR
            raise ValidationError(msg)

        return payload

    def _check_user(self, payload):
        """
        :rtype: object
        """
        global user
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = INVALID_PAYLOAD
            raise ValidationError(msg)

        # Make sure user exists
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            msg = INVALID_USER
            raise ValidationError(msg)

        if not user.is_active:
            msg = DISABLED_USER_ACCOUNT
            raise ValidationError(msg)

        return user

    def get_info(self, token: str) -> str:
        """
        :param token:
        :return:
        """
        payload = self._check_payload(token=token)
        user_obj = self._check_user(payload=payload)
        user_serializer = UserSerializer(user_obj)
        return user_serializer.data


'''
#---------------------------------------------------------------------------------------#
|                                                                                       |
|                                                                                       |
|           Create Token and return response for both User and Vendor            |
|                                                                                       |
|                                                                                       |
#---------------------------------------------------------------------------------------#
'''


class CreateTokenResponse:
    def __init__(self, user, orig_iat=None, request=None):
        """
        :param user:
        :param orig_iat:
        :param request:
        """
        self.user = user
        self.orig_iat = orig_iat
        self.request = request

    def jwt_response_payload_handler(self, token, user=None, request=None):
        """
        :param token:
        :param user:
        :param request:
        :return:
        """
        user = UserSerializer(user).data
        return {'token': token, 'user': user}

    def get_response(self):
        """
        :return: user info and token
        """
        payload = jwt_payload_handler(self.user)
        if self.orig_iat:
            payload['orig_iat'] = self.orig_iat

        token = jwt_encode_handler(payload)

        response_data = self.jwt_response_payload_handler(token, self.user, self.request)
        return response_data, token


'''
#---------------------------------------------------------------------------------------#
|                                                                                       |
|                                                                                       |
|                       Try to logged In for General User                               |
|                                                                                       |
|                                                                                       |
#---------------------------------------------------------------------------------------#
'''


class LoginUserToken(ObtainJSONWebToken):
    """
        Generate a token for service user
    """

    @method_decorator(check_user)
    def post(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            # get user from decorator
            if User.objects.filter(username=request.data['username']).exists():
                user = User.objects.authenticate(username=request.data['username'], password=request.data['password'])
            elif User.objects.filter(email=request.data['username']).exists():
                user = User.objects.authenticate(email=request.data['username'], password=request.data['password'])

            token_res = CreateTokenResponse(user=user, request=request)
            response_data, token = token_res.get_response()
            response = Response(response_data, status=status.HTTP_200_OK)

            # check if token time has expired
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE, token, expires=expiration, httponly=True)

        except Exception as e:
            raise e

        return response


class ObtainRefreshToken(JSONWebTokenAPIView):
    """
    Refresh an access token.
    """

    def post(self, request, *args, **kwargs):
        """
        :param request: request from frontend
        :param args:
        :param kwargs:
        :return: user token and user info
        """
        user_info_obj = GetUserInfo()

        token = request.data['token']
        payload = user_info_obj._check_payload(token=token)
        user = user_info_obj._check_user(payload=payload)
        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')

        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 + refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = EXPIRED_REFRESH
                raise ValidationError(msg)
        else:
            msg = REQUIRED_ORIGIN_IAT_FIELD
            raise ValidationError(msg)

        token_res = CreateTokenResponse(user=user, orig_iat=orig_iat, request=request)
        response_data, token = token_res.get_response()

        return Response(response_data, status=status.HTTP_200_OK)


get_jwt_token_for_login_user = LoginUserToken.as_view()
refresh_jwt_token = ObtainRefreshToken().as_view()
