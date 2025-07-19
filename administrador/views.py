from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .administrator_service import AdministratorService
from .forms import CrearUsuarioForm

@login_required
def crear_usuario_view(request):
    """Vista para crear usuarios (solo para jefes de seguridad)"""
    if request.user.rol != 'jefe':
        messages.error(request, 'No tiene permisos para acceder a esta función')
        return redirect('dashboard_jefe')
    
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            try:
                usuario = AdministratorService.crear_usuario(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    nombre=form.cleaned_data['nombre'],
                    rol=form.cleaned_data['rol']
                )
                
                if hasattr(usuario, 'correo_enviado') and usuario.correo_enviado:
                    messages.success(request, f'Usuario {usuario.username} creado exitosamente. Se ha enviado un correo con las credenciales a {usuario.email}')
                else:
                    # El usuario se creó pero el correo falló
                    contraseña_temp = getattr(usuario, 'contraseña_temporal', 'No disponible')
                    messages.warning(request, f'Usuario {usuario.username} creado exitosamente, pero hubo un problema enviando el correo. Contraseña temporal: {contraseña_temp}')
                
                return redirect('administrador:crear_usuario')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = CrearUsuarioForm()
    
    return render(request, 'administrador/crear_usuario.html', {'form': form})

@login_required
def listar_usuarios_view(request):
    """Vista para listar todos los usuarios"""
    if request.user.rol != 'jefe':
        messages.error(request, 'No tiene permisos para acceder a esta función')
        return redirect('dashboard_jefe')
    
    usuarios = AdministratorService.listar_usuarios()
    estadisticas = AdministratorService.obtener_estadisticas()
    
    return render(request, 'administrador/listar_usuarios.html', {
        'usuarios': usuarios,
        'estadisticas': estadisticas
    })

@login_required
def dashboard_admin(request):
    """Dashboard principal del administrador"""
    if request.user.rol != 'jefe':
        messages.error(request, 'No tiene permisos para acceder a esta función')
        return redirect('login')
    
    estadisticas = AdministratorService.obtener_estadisticas()
    usuarios_recientes = AdministratorService.listar_usuarios()[:5]
    
    return render(request, 'administrador/dashboard_admin.html', {
        'estadisticas': estadisticas,
        'usuarios_recientes': usuarios_recientes
    })
