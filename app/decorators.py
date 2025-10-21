from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def group_required(*group_names):
    """
    Decorador que verifica si el usuario pertenece a alguno de los grupos especificados.
    Redirige a la página 'portal' y muestra un mensaje si no pertenece.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.groups.filter(name__in=group_names).exists() or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "No tienes permiso para acceder a esta página.")
                return redirect('portal')
        return _wrapped_view
    return decorator