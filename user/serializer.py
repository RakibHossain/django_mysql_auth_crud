from django.core import exceptions
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from applibs.utils import check_unique_username, check_unique_email
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uuid', 'name', 'username', 'email', 'is_active')


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('uuid', 'name', 'username', 'email', 'password')

    def validate(self, data):
        name = data.get("name", "")
        username = data.get("username", "")
        email = data.get("email", "")
        password = data.get("password", "")
        conf_password = data.get("confirm_password", "")

        message = {}
        if username:
            is_unique = check_unique_username(username)
            if not is_unique:
                msg = ["Account already exists with this username"]
                message['username'] = msg
        else:
            msg = ["Username not found"]
            message['username'] = msg

        if email:
            is_unique = check_unique_email(email)
            if not is_unique:
                msg = ["Account already exists with this email"]
                message['email'] = msg
        else:
            msg = ["Email not found"]
            message['email'] = msg

        if password:
            # TODO: check strength
            if password != conf_password:
                msg = ["Password and Confirm Password mismatch"]
                message['password'] = msg
            pass
        else:
            msg = ["Password not found"]
            message['password'] = msg

        if message:
            raise serializers.ValidationError(message)

        return data
