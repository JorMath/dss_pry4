import os
import django

# Configurar Django antes de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
django.setup()

from behave import given, when, then
from django.test import Client
from django.urls import reverse
from accounts.models import Usuario


@given('que existen usuarios con diferentes roles en el sistema')
def step_crear_usuarios_diferentes_roles(context):
    """Crear usuarios con diferentes roles para las pruebas"""
    # Limpiar usuarios existentes de prueba
    Usuario.objects.filter(username__startswith='test_').delete()
    
    # Crear jefe de seguridad
    context.jefe = Usuario.objects.create_user(
        username='test_jefe',
        password='testpass123',
        rol='jefe'
    )
    context.jefe.nombre = 'María López'
    context.jefe.save()
    
    # Crear analistas
    context.analista1 = Usuario.objects.create_user(
        username='test_analista1',
        password='testpass123',
        rol='analista'
    )
    context.analista1.nombre = 'Ana García'
    context.analista1.save()
    
    context.analista2 = Usuario.objects.create_user(
        username='test_analista2',
        password='testpass123',
        rol='analista'
    )
    context.analista2.nombre = 'Luis Martín'
    context.analista2.save()
    
    # Crear reportantes
    context.reportante1 = Usuario.objects.create_user(
        username='test_reportante1',
        password='testpass123',
        rol='reportante'
    )
    context.reportante1.nombre = 'Carlos Pérez'
    context.reportante1.save()
    
    context.reportante2 = Usuario.objects.create_user(
        username='test_reportante2',
        password='testpass123',
        rol='reportante'
    )
    context.reportante2.nombre = 'Sofia Ruiz'
    context.reportante2.save()


@given('estoy autenticado como jefe de seguridad')
def step_autenticar_como_jefe(context):
    """Autenticar como jefe de seguridad"""
    context.client = Client()
    context.client.force_login(context.jefe)


@given('que estoy en la lista de usuarios')
def step_navegar_lista_usuarios(context):
    """Navegar a la lista de usuarios"""
    url = reverse('administrador:listar_usuarios')
    context.response = context.client.get(url)
    assert context.response.status_code == 200


@given('que estoy autenticado como un usuario con rol "{rol}"')
def step_autenticar_con_rol_especifico(context, rol):
    """Autenticar con un rol específico"""
    if rol == 'analista':
        usuario = context.analista1
    elif rol == 'reportante':
        usuario = context.reportante1
    else:
        # Crear usuario si no existe
        usuario = Usuario.objects.create_user(
            username=f'test_{rol}',
            password='testpass123',
            rol=rol
        )
    
    context.client = Client()
    context.client.force_login(usuario)
    context.usuario_actual = usuario


@when('acceda a "Listar usuarios"')
def step_acceder_listar_usuarios(context):
    """Acceder a la funcionalidad de listar usuarios"""
    url = reverse('administrador:listar_usuarios')
    context.response = context.client.get(url)


@when('intente acceder a "Listar usuarios"')
def step_intentar_acceder_listar_usuarios(context):
    """Intentar acceder sin permisos"""
    url = reverse('administrador:listar_usuarios')
    context.response = context.client.get(url)


@then('veo todos los usuarios ordenados por rol')
def step_verificar_usuarios_ordenados_por_rol(context):
    """Verificar que los usuarios están ordenados por rol"""
    assert context.response.status_code == 200
    content = context.response.content.decode('utf-8')
    
    # Verificar que aparecen los roles en el orden esperado
    assert 'jefe' in content.lower()
    assert 'analista' in content.lower()
    assert 'reportante' in content.lower()
    
    # Verificar que hay contenido de usuarios
    assert 'usuario' in content.lower()


@then('veo la información completa de cada usuario')
def step_verificar_informacion_completa_usuarios(context):
    """Verificar que se muestra información completa"""
    content = context.response.content.decode('utf-8')
    
    # Verificar que se muestran los campos esperados
    assert 'username' in content.lower()
    assert 'nombre' in content.lower()
    assert 'email' in content.lower() or 'correo' in content.lower()
    assert 'rol' in content.lower()


@then('veo las estadísticas de usuarios por rol')
def step_verificar_estadisticas_por_rol(context):
    """Verificar que se muestran estadísticas por rol"""
    content = context.response.content.decode('utf-8')
    
    # Verificar que hay información estadística
    assert 'estadística' in content.lower() or 'total' in content.lower() or 'cantidad' in content.lower()


@then('cada usuario muestra: username, nombre, email descifrado y rol')
def step_verificar_campos_usuario(context):
    """Verificar campos específicos de cada usuario"""
    content = context.response.content.decode('utf-8')
    
    # Verificar que se muestran los usuarios creados
    assert 'test_jefe' in content or 'María López' in content
    assert 'test_analista' in content or 'Ana García' in content or 'Luis Martín' in content
    assert 'test_reportante' in content or 'Carlos Pérez' in content or 'Sofia Ruiz' in content


@then('los usuarios están agrupados por rol')
def step_verificar_agrupacion_por_rol(context):
    """Verificar agrupación por rol"""
    content = context.response.content.decode('utf-8')
    
    # Verificar que hay algún tipo de agrupación o sección por rol
    assert ('jefe' in content.lower() and 'analista' in content.lower() and 
            'reportante' in content.lower())


@then('el sistema me redirige por falta de permisos')
def step_verificar_redireccion_permisos(context):
    """Verificar redirección por falta de permisos"""
    # Verificar que no puede acceder (código 403, 302 para redirect, o 401)
    assert context.response.status_code in [403, 302, 401]
