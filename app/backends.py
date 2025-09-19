from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Perfil

class RUTBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            perfil = Perfil.objects.get(rut=username)
            user = perfil.user
            if user.check_password(password):
                return user
        except Perfil.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None