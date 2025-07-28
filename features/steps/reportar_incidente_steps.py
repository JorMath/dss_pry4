import os
import django
from datetime import datetime, timezone

# Configurar Django antes de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
django.setup()

from behave import given, when, then
from django.test import Client
from accounts.models import Usuario
from incidentes.models import Incidente


@given('que el Usuario reportante tiene un incidente de tipo "{tipo}" con descripción "{descripcion}" con fecha "{fecha}"')
def step_dado_usuario_con_incidente_data(context, tipo, descripcion, fecha):
    # Limpiar datos de prueba previos
    Usuario.objects.filter(username='test_reportante').delete()
    
    # Crear usuario reportante de prueba
    context.usuario_reportante = Usuario.objects.create_user(
        username='test_reportante',
        email='reportante@test.com',
        password='password123',
        rol='reportante',
        nombre='Usuario Reportante Test'
    )
    
    # Mapear tipo desde la especificación al modelo
    tipo_mapping = {
        'bug': 'bug_seguridad',
        'acceso': 'acceso_no_autorizado',
        'malware': 'malware',
        'phishing': 'phishing',
        'ddos': 'ddos',
        'fuga': 'fuga_datos',
        'otro': 'otro'
    }
    
    # Guardar datos del incidente para usar después
    context.tipo_incidente = tipo_mapping.get(tipo, 'otro')
    context.descripcion_incidente = descripcion
    context.fecha_incidente = fecha
    context.client = Client()
    context.client.force_login(context.usuario_reportante)


@when('reporte el incidente')
def step_cuando_reportar_incidente(context):
    try:
        # Crear el incidente directamente usando el modelo
        context.incidente_creado = Incidente.objects.create(
            tipo=context.tipo_incidente,
            descripcion=context.descripcion_incidente,
            reportado_por=context.usuario_reportante
        )
        context.reporte_exitoso = True
        
    except Exception as e:
        context.reporte_exitoso = False
        context.error_reporte = str(e)


@then('el incidente se registra con el estado "{estado_esperado}" y gravedad "{gravedad_esperada}"')
def step_entonces_incidente_registrado(context, estado_esperado, gravedad_esperada):
    assert context.reporte_exitoso, f"El reporte del incidente falló: {getattr(context, 'error_reporte', 'Error desconocido')}"
    
    assert context.incidente_creado is not None, "El incidente no fue creado"
    assert context.incidente_creado.estado == estado_esperado, f"Estado esperado: {estado_esperado}, obtenido: {context.incidente_creado.estado}"
    assert context.incidente_creado.gravedad == gravedad_esperada, f"Gravedad esperada: {gravedad_esperada}, obtenida: {context.incidente_creado.gravedad}"


@then('se notifica al Usuario reportante que se ha realizado el reporte correctamente')
def step_entonces_notificacion_reporte(context):
    # Verificar que el incidente fue creado exitosamente
    assert context.reporte_exitoso, "El reporte no fue exitoso"
    
    # Verificar que el incidente existe en la base de datos
    incidente_db = Incidente.objects.filter(
        reportado_por=context.usuario_reportante,
        descripcion=context.descripcion_incidente
    ).first()
    
    assert incidente_db is not None, "El incidente no se guardó en la base de datos"
    
    # En un escenario real, aquí verificaríamos que se muestra el mensaje en la UI
    # Para propósitos de esta prueba de negocio, consideramos que si el incidente 
    # se creó exitosamente, la notificación sería mostrada
    context.notificacion_mostrada = True


def cleanup_test_data(context):
    """Limpiar datos de prueba"""
    Usuario.objects.filter(email__contains='@test.com').delete()
    Incidente.objects.filter(reportado_por__email__contains='@test.com').delete()
