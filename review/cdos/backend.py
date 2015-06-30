from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class OAuthBackend(ModelBackend):
    def authenticate(self, openid):
        return User.objects.get(id=openid)


class UserBackend(ModelBackend):
    def authenticate(self, user):
        return user
