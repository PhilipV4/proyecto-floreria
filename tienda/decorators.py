from functools import wraps
from django.shortcuts import redirect

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificamos si está autenticado y si su rol está dentro de los permitidos
            if request.user.is_authenticated and getattr(request.user, 'role', None) in roles:
                return view_func(request, *args, **kwargs)
            return redirect('/')  # Redirige al inicio si no tiene permisos
        return wrapper
    return decorator