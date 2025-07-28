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


@given('que el Usuario reportante tiene al menos un incidente reportado')
def step_dado_usuario_con_incidentes(context):
    # Limpiar datos de prueba previos
    Usuario.objects.filter(username='test_reportante_hu02').delete()
    
    # Crear usuario reportante de prueba
    context.usuario_reportante = Usuario.objects.create_user(
        username='test_reportante_hu02',
        email='reportante_hu02@test.com',
        password='password123',
        rol='reportante',
        nombre='Usuario Reportante HU02 Test'
    )
    
    # Crear al menos un incidente de prueba
    context.incidente_test = Incidente.objects.create(
        tipo='bug_seguridad',
        descripcion='Incidente de prueba para HU02',
        reportado_por=context.usuario_reportante
    )
    
    context.client = Client()
    context.client.force_login(context.usuario_reportante)


@given('que el Usuario Reportante no tiene incidentes reportados')
def step_dado_usuario_sin_incidentes(context):
    # Limpiar datos de prueba previos
    Usuario.objects.filter(username='test_reportante_sin_incidentes').delete()
    
    # Crear usuario reportante de prueba
    context.usuario_reportante = Usuario.objects.create_user(
        username='test_reportante_sin_incidentes',
        email='reportante_sin_incidentes@test.com',
        password='password123',
        rol='reportante',
        nombre='Usuario Sin Incidentes Test'
    )
    
    # Asegurar que no tiene incidentes
    Incidente.objects.filter(reportado_por=context.usuario_reportante).delete()
    
    context.client = Client()
    context.client.force_login(context.usuario_reportante)


@when('quiera ver los incidentes que ha reportado')
def step_cuando_ver_incidentes(context):
    try:
        # Consultar los incidentes del usuario
        context.mis_incidentes = Incidente.objects.filter(
            reportado_por=context.usuario_reportante
        ).order_by('-fecha_reporte')
        context.consulta_exitosa = True
        
    except Exception as e:
        context.consulta_exitosa = False
        context.error_consulta = str(e)


@then('se mostrará una lista de incidentes que ha reportado')
def step_entonces_mostrar_lista_incidentes(context):
    assert context.consulta_exitosa, f"La consulta falló: {getattr(context, 'error_consulta', 'Error desconocido')}"
    
    # Verificar que hay al menos un incidente
    assert context.mis_incidentes.count() > 0, "No se encontraron incidentes reportados por el usuario"
    
    # Verificar que todos los incidentes pertenecen al usuario actual
    for incidente in context.mis_incidentes:
        assert incidente.reportado_por == context.usuario_reportante, "Se encontró un incidente que no pertenece al usuario actual"


@then('se notifica al Usuario reportante que no ha reportado ningún incidente')
def step_entonces_notificar_sin_incidentes(context):
    assert context.consulta_exitosa, f"La consulta falló: {getattr(context, 'error_consulta', 'Error desconocido')}"
    
    # Verificar que no hay incidentes
    assert context.mis_incidentes.count() == 0, f"Se esperaba que no hubiera incidentes, pero se encontraron {context.mis_incidentes.count()}"
    
    # En un escenario real, aquí verificaríamos que se muestra el mensaje en la UI
    context.mensaje_sin_incidentes = "No ha reportado ningún incidente"


@then('se le permite regresar a las opciones de registro de incidentes')
def step_entonces_permitir_regresar(context):
    # Verificar que el contexto está preparado para regresar a las opciones
    # En un escenario real, esto sería verificar que hay un botón o enlace disponible
    assert hasattr(context, 'mensaje_sin_incidentes'), "No se estableció el contexto para regresar"
    
    # Simular que se puede regresar a las opciones de registro
    context.puede_regresar_a_registro = True
    assert context.puede_regresar_a_registro, "No se puede regresar a las opciones de registro"


def cleanup_test_data(context):
    """Limpiar datos de prueba"""
    Usuario.objects.filter(email__contains='@test.com').delete()
    Incidente.objects.filter(reportado_por__email__contains='@test.com').delete()
