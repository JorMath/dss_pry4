# accounts/decorators.py
from django.shortcuts import redirect

def rol_required(rol):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rol == rol:
                return view_func(request, *args, **kwargs)
            return redirect('login')
        return _wrapped_view
    return decorator
