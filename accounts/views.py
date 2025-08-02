from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm, ForgotPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .decorators import rol_required
from administrador.administrator_service import AdministratorService
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from django_ratelimit import UNSAFE
from django_ratelimit.core import is_ratelimited
from django.http import HttpResponseForbidden

def rate_limit_exceeded_view(request):
    """Vista personalizada para mostrar cuando se excede el rate limit de login"""
    return render(request, 'accounts/rate_limit_exceeded.html')

def forgot_password_rate_limit_view(request):
    """Vista personalizada para mostrar cuando se excede el rate limit de forgot password"""
    return render(request, 'accounts/forgot_password_rate_limit.html')

def _redirect_by_role(user):
    """Función auxiliar para redireccionar usuarios según su rol"""
    if user.rol == 'reportante':
        return redirect('dashboard_reportante')
    elif user.rol == 'analista':
        return redirect('dashboard_analista')
    elif user.rol == 'jefe':
        return redirect('dashboard_jefe')
    return redirect('dashboard_reportante')  # fallback por defecto

@ratelimit(key='ip', rate='5/5m', method='POST', block=False)
@ratelimit(key='user_or_ip', rate='10/h', method='POST', block=False)
def login_view(request):
    # Verificar si el usuario está siendo rate limited
    if request.method != 'POST':
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})
    
    # Verificar rate limit antes de procesar
    if getattr(request, 'limited', False):
        return redirect('rate_limit_exceeded')
    
    form = LoginForm(request.POST)
    if not form.is_valid():
        return render(request, 'accounts/login.html', {'form': form})
    
    usuario = form.cleaned_data['username']
    password = form.cleaned_data['password']
    user = authenticate(request, username=usuario, password=password)
    
    if user is not None:
        login(request, user)
        return _redirect_by_role(user)
    else:
        messages.error(request, 'Credenciales incorrectas')
        return render(request, 'accounts/login.html', {'form': form})
@login_required
@rol_required('jefe')
def dashboard_jefe(request):
    from .models import Usuario
    from incidentes.models import Incidente
    from django.utils import timezone
    from datetime import datetime
    
    # Obtener estadísticas de usuarios
    total_usuarios = Usuario.objects.count()
    usuarios_analistas = Usuario.objects.filter(rol='analista').count()
    usuarios_reportantes = Usuario.objects.filter(rol='reportante').count()
    usuarios_jefes = Usuario.objects.filter(rol='jefe').count()
    
    # Estadísticas de incidentes
    total_incidentes = Incidente.objects.count()
    incidentes_pendientes = Incidente.objects.filter(estado='pendiente').count()
    incidentes_criticos = Incidente.objects.filter(gravedad='critica').count()
    
    # Incidentes del mes actual
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    incidentes_mes_actual = Incidente.objects.filter(
        fecha_reporte__month=mes_actual,
        fecha_reporte__year=anio_actual
    ).count()
    
    stats = {
        'total_usuarios': total_usuarios,
        'jefes': usuarios_jefes,
        'analistas': usuarios_analistas,
        'reportantes': usuarios_reportantes,
        'total_incidentes': total_incidentes,
        'incidentes_pendientes': incidentes_pendientes,
        'incidentes_criticos': incidentes_criticos,
        'incidentes_mes_actual': incidentes_mes_actual,
    }
    
    context = {
        'usuario': request.user,
        'stats': stats,
    }
    
    return render(request, 'accounts/dashboard_jefe.html', context)

@login_required
@rol_required('analista')
def dashboard_analista(request):
    return render(request, 'accounts/dashboard_analista.html', {'usuario': request.user})

@login_required
@rol_required('reportante')
def dashboard_reportante(request):
    return render(request, 'accounts/dashboard_reportante.html', {'usuario': request.user})

def logout_view(request):
    logout(request)
    return redirect('login')

@ratelimit(key='ip', rate='3/10m', method='POST', block=False)
@ratelimit(key='user_or_ip', rate='5/h', method='POST', block=False)
def forgot_password_view(request):
    if request.method == 'POST':
        # Verificar rate limit antes de procesar
        if getattr(request, 'limited', False):
            return redirect('forgot_password_rate_limit')
        
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                # Usar el servicio de administrador para restablecer contraseña
                resultado = AdministratorService.restablecer_contrasenia(email)
                
                if resultado['success']:
                    if resultado['correo_enviado']:
                        messages.success(
                            request, 
                            'Se ha enviado una nueva contraseña temporal a tu correo electrónico.'
                        )
                    else:
                        messages.warning(
                            request,
                            'Se generó una nueva contraseña, pero hubo un problema enviando el correo. Contacta al administrador.'
                        )
                    return redirect('login')
                    
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})
