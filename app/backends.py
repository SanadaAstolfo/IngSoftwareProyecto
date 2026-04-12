from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Perfil

class RUTBackend(ModelBackend):
    def normalize_rut(self, rut):
        # Normaliza el RUT eliminando puntos y guiones
        if rut:
            return rut.replace('.', '').replace('-', '').upper()
        return rut
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Normalizar el RUT ingresado
        normalized_username = self.normalize_rut(username)
        
        # Primero intentar autenticar por RUT (buscando en Perfil)
        try:
            # Buscar en todos los perfiles normalizando el RUT
            for perfil in Perfil.objects.all():
                if self.normalize_rut(perfil.rut) == normalized_username:
                    user = perfil.user
                    if user.check_password(password):
                        return user
        except Exception:
            pass
        
        # Si no funciona por RUT, intentar por username normal (para staff)
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        
        # También intentar con el username normalizado
        try:
            # Buscar usuarios cuyo username normalizado coincida
            for user in User.objects.all():
                if self.normalize_rut(user.username) == normalized_username:
                    if user.check_password(password):
                        return user
        except Exception:
            pass
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None