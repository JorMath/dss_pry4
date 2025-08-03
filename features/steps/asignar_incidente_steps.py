import os
import django

# Configurar Django antes de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
django.setup()

from behave import given, when, then
from django.test import Client
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import Usuario
from incidentes.models import Incidente


@given('que existen usuarios: jefe "{jefe_nombre}", analistas "{analista1_nombre}" y "{analista2_nombre}"')
def step_crear_usuarios_basicos(context, jefe_nombre, analista1_nombre, analista2_nombre):
    """Crear usuarios básicos para las pruebas"""
    # Limpiar usuarios existentes
    Usuario.objects.filter(username__in=['test_jefe', 'test_analista1', 'test_analista2']).delete()
    
    # Crear jefe
    context.jefe = Usuario.objects.create_user(
        username='test_jefe',
        password='testpass123',
        rol='jefe'
    )
    context.jefe.nombre = jefe_nombre
    context.jefe.save()
    
    # Crear analistas
    context.analista1 = Usuario.objects.create_user(
        username='test_analista1',
        password='testpass123',
        rol='analista'
    )
    context.analista1.nombre = analista1_nombre
    context.analista1.save()
    
    context.analista2 = Usuario.objects.create_user(
        username='test_analista2',
        password='testpass123',
        rol='analista'
    )
    context.analista2.nombre = analista2_nombre
    context.analista2.save()


@given('existe un incidente pendiente ID "{incidente_id}"')
def step_crear_incidente_pendiente(context, incidente_id):
    """Crear incidente pendiente"""
    # Crear reportante si no existe
    if not hasattr(context, 'reportante'):
        context.reportante = Usuario.objects.create_user(
            username='test_reportante',
            password='testpass123',
            rol='reportante'
        )
    
    context.incidente_pendiente = Incidente.objects.create(
        id=int(incidente_id),
        tipo='acceso_no_autorizado',
        descripcion='Incidente de prueba pendiente',
        estado='pendiente',
        reportado_por=context.reportante,
        gravedad='media'
    )


@given('existe un incidente asignado ID "{incidente_id}" a "{analista_nombre}"')
def step_crear_incidente_asignado(context, incidente_id, analista_nombre):
    """Crear incidente ya asignado"""
    # Crear reportante si no existe
    if not hasattr(context, 'reportante'):
        context.reportante = Usuario.objects.create_user(
            username='test_reportante',
            password='testpass123',
            rol='reportante'
        )
    
    analista = Usuario.objects.filter(nombre=analista_nombre).first()
    context.incidente_asignado = Incidente.objects.create(
        id=int(incidente_id),
        tipo='phishing',
        descripcion='Incidente de prueba asignado',
        estado='en_progreso',
        reportado_por=context.reportante,
        asignado_a=analista,
        gravedad='alta'
    )


@given('estoy autenticado como jefe de seguridad')
def step_autenticar_jefe(context):
    """Autenticar como jefe de seguridad"""
    context.client = Client()
    context.client.force_login(context.jefe)


@given('que estoy en la lista de incidentes')
def step_navegar_lista_incidentes(context):
    """Navegar a la lista de incidentes"""
    url = reverse('incidentes:todos_incidentes')
    context.response = context.client.get(url)
    assert context.response.status_code == 200


@when('asigne el incidente "{incidente_id}" al analista "{analista_nombre}"')
def step_asignar_incidente(context, incidente_id, analista_nombre):
    """Asignar incidente a analista"""
    analista = Usuario.objects.filter(nombre=analista_nombre).first()
    incidente = Incidente.objects.get(id=int(incidente_id))
    
    url = reverse('incidentes:asignar_incidente', args=[incidente.id])
    data = {'asignado_a': analista.id}
    
    context.fecha_antes = incidente.fecha_actualizacion
    context.response = context.client.post(url, data)
    
    # Recargar incidente
    incidente.refresh_from_db()
    context.incidente_actualizado = incidente


@when('reasigne el incidente "{incidente_id}" de "{analista_anterior}" a "{analista_nuevo}"')
def step_reasignar_incidente(context, incidente_id, analista_anterior, analista_nuevo):
    """Reasignar incidente"""
    analista = Usuario.objects.filter(nombre=analista_nuevo).first()
    incidente = Incidente.objects.get(id=int(incidente_id))
    
    url = reverse('incidentes:asignar_incidente', args=[incidente.id])
    data = {'asignado_a': analista.id}
    
    context.fecha_antes = incidente.fecha_actualizacion
    context.response = context.client.post(url, data)
    
    # Recargar incidente
    incidente.refresh_from_db()
    context.incidente_actualizado = incidente


@then('el incidente queda asignado a "{analista_nombre}"')
def step_verificar_asignacion(context, analista_nombre):
    """Verificar asignación exitosa"""
    incidente = context.incidente_actualizado
    assert incidente.asignado_a is not None
    assert incidente.asignado_a.nombre == analista_nombre


@then('se confirma con mensaje de éxito')
def step_verificar_mensaje_exito(context):
    """Verificar mensaje de confirmación"""
    messages = list(get_messages(context.response.wsgi_request))
    assert len(messages) > 0
    assert any('asignado' in str(message).lower() for message in messages)


@then('el incidente cambia de asignación a "{analista_nombre}"')
def step_verificar_reasignacion(context, analista_nombre):
    """Verificar reasignación exitosa"""
    incidente = context.incidente_actualizado
    assert incidente.asignado_a.nombre == analista_nombre


@then('se confirma la reasignación')
def step_verificar_mensaje_reasignacion(context):
    """Verificar mensaje de reasignación"""
    messages = list(get_messages(context.response.wsgi_request))
    assert len(messages) > 0
    message_text = ' '.join(str(message) for message in messages)
    assert 'asignado' in message_text.lower()


@then('veo la columna "Asignado a"')
def step_verificar_columna_asignado(context):
    """Verificar columna de asignación"""
    content = context.response.content.decode('utf-8')
    assert 'asignado a' in content.lower()


@then('los incidentes muestran su estado de asignación')
def step_verificar_estado_asignacion(context):
    """Verificar visualización del estado"""
    content = context.response.content.decode('utf-8')
    # Verificar elementos visuales de asignación
    assert 'assigned-info' in content or 'unassigned-info' in content
    assert 'fa-user-check' in content or 'fa-user-times' in content
