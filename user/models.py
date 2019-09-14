import uuid as uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from applibs.response_status_code import *
from applibs.generator import password_encrypt
from applibs.utils import check_unique_username, check_unique_email

# Create your models here.

class UserManager(models.Manager):

    # def update_user(self, username, data):
    #     user = self.get_user_by_username(username)
    #     if not user:
    #         return {'error_code': USER_PROFILE_NOT_FOUND}, 403

    #     if 'username' in data:
    #         new_username = data['username']
    #         # check conflict
    #         if user.username == str(new_username).strip():
    #             return {'error_code': USER_USERNAME_NOT_MODIFIED}, 304
    #         is_username_conflict = check_unique_username(new_username)
    #         if is_username_conflict:
    #             return {'error_code': USER_USERNAME_CONFLICT}, 400
    #         change = self.filter(username=username).update(username=new_username)
    #         return {'success_code': USER_USERNAME_UPDATED}, 201
    #     elif 'email' in data:
    #         new_email = data['email']
    #         # check conflict
    #         if user.email == str(new_email).strip():
    #             return {'success_code': USER_EMAIL_NOT_MODIFIED}, 304
    #         is_email_conflict = check_unique_email(new_email)
    #         if is_email_conflict:
    #             return {'success_code': USER_EMAIL_CONFLICT}, 400
    #         change = self.filter(username=username).update(email=new_email)
    #         return {'success_code': USER_EMAIL_UPDATED}, 201
    #     elif 'password' in data:
    #         new_password = data['password']
    #         # check password strength
    #         change = self.filter(username=username).update(password=password_encrypt(new_password))
    #         return {'success_code': USER_PASSWORD_UPDATED}, 201
    #     else:
    #         return '', 200

    # get all users
    def all_user(self):
        return self.filter(is_active=True, is_deleted=False)

    def active_user(self, uuid):
        return self.filter(uuid=uuid).update(is_active=True)

    # Delete User
    def remove_user(self, username):
        return self.filter(username=username).update(is_active=False, is_deleted=True)

    def check_auth_user(self, username, password):
        return self.filter(username=username, password=password)[:1]

    def authenticate(self, username=None, email=None, password=None):
        try:
            if username:
                return self.get(username=username, password=password_encrypt(password))
            elif email:
                return self.get(email=email, password=password_encrypt(password))
        except ObjectDoesNotExist:
            return False

    def get_user(self, uuid):
        try:
            return self.get(uuid=uuid, is_active=True)
        except ObjectDoesNotExist:
            return False

    def get_user_by_username(self, username):
        try:
            return self.get(username=username, is_active=True)
        except ObjectDoesNotExist:
            return False

    def get_user_by_email(self, email):
        try:
            return self.get(email=email, is_active=True)
        except ObjectDoesNotExist:
            return False

    def create_user(self, data):
        return self.create(name=data['name'], username=data['username'], email=data['email'], password=password_encrypt(data['password']), is_active=True)

    def update_user(self, username, data):
        req_data_fields = ['name', 'username', 'email', 'password']
        kwrgs = {}
        for field in data:
            if field in req_data_fields:
                if field == 'password':
                    kwrgs['password'] = password_encrypt(data['password'])
                else:
                    kwrgs[field] = data[field]

        if kwrgs:
            # update user
            self.filter(username=username).update(**kwrgs)
            return {'success_code': USER_UPDATED}, 201

        return {'error_code': USER_KEY_ERROR}, 400


class User(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, default=False)
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=250)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    def __str__(self):
        return "User {username} created at {created_at}".format(
            username=self.username,
            created_at=self.created_at
        )
