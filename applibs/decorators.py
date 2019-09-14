import json
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from applibs.response_messages import *

# create custom 401 Unauthorized
from user.models import User


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


def check_user(func):
    """
    Decorator to authenticate a user
    :param: func: support user checking for token
    """

    def wrapper(request, *args, **kwargs):

        if "username" not in request.data or "password" not in request.data:
            return HttpResponseBadRequest(json.dumps({"message": DONT_KNOW_ANYTHING}))

        if "username" in request.data and "password" in request.data:
            username = request.data.get("username", request.user)
            password = request.data["password"]

            # User existance check
            # check user is registered
            exist = True
            username_contain = True
            
            if not User.objects.filter(username=username).exists():
                exist = False
                username_contain = False

            if not exist:
                if not User.objects.filter(email=username).exists():
                    return HttpResponseBadRequest(json.dumps({"message": USER_NOT_FOUND}))

            # Check user is activated or not
            if username_contain:
                if User.objects.filter(username=username).exists():
                    if not User.objects.get(username=username).is_active:
                        return HttpResponseBadRequest(json.dumps({"message": INACTIVATED_USER}))
            else:
                if User.objects.filter(email=username).exists():
                    if not User.objects.get(email=username).is_active:
                        return HttpResponseBadRequest(json.dumps({"message": INACTIVATED_USER}))

            # Check user credentials
            if username_contain:
                user = User.objects.authenticate(username=username, password=password)
            else:
                user = User.objects.authenticate(email=username, password=password)

            if not user:
                return HttpResponseUnauthorized(json.dumps({"message": INVALID_USER_INFO}))

            return func(request, *args, **kwargs)

        else:
            return HttpResponseBadRequest(json.dumps({"message": INVALID_DATA}))

    return wrapper
