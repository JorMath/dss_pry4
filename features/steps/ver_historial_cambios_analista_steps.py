from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from incidentes.models import Incidente, HistorialCambioIncidente
from accounts.models import Usuario

User = get_user_model()

@given('existe un incidente con historial de cambios')
def step_impl(context):
    # Intentar obtener el reportante existente o crear uno nuevo
    try:
        context.reportante = Usuario.objects.get(username='reportante_test')
    except Usuario.DoesNotExist:
        context.reportante = Usuario.objects.create_user(
            username='reportante_test',
            password='password123',
            nombre='Reportante Test',
            rol='empleado'
        )
    
    # Crear incidente para este escenario específico
    context.incidente = Incidente.objects.create(
        tipo='bug_seguridad',
        descripcion='Incidente de prueba para historial',
        reportado_por=context.reportante,
        estado='pendiente',
        gravedad='baja'
    )
    
    # Crear algunos cambios en el historial para el escenario específico
    HistorialCambioIncidente.objects.create(
        incidente=context.incidente,
        usuario_modificacion=context.analista,
        campo_modificado='Estado',
        valor_anterior='pendiente',
        valor_nuevo='en_proceso'
    )
    
    HistorialCambioIncidente.objects.create(
        incidente=context.incidente,
        usuario_modificacion=context.analista,
        campo_modificado='Gravedad',
        valor_anterior='baja',
        valor_nuevo='alta'
    )

@given('que se tiene al menos un incidente')
def step_impl(context):
    # El incidente ya está creado
    pass

@when('el analista desee ver los detalles de ese incidente')
def step_impl(context):
    context.response = context.client.get(
        reverse('incidentes:historial_incidente', args=[context.incidente.id])
    )

@then('verá una lista con todas las modificaciones registradas incluyendo el analista que lo modificó, la descripción, tipo, gravedad y estado')
def step_impl(context):
    assert context.response.status_code == 200
    response_content = context.response.content.decode()
    
    # Verificar que se muestran todos los elementos requeridos del escenario
    assert 'Analista Test' in response_content  # Analista que modificó
    assert context.incidente.descripcion in response_content  # Descripción
    assert context.incidente.get_tipo_display() in response_content  # Tipo
    
    # Verificar que aparecen los cambios de gravedad y estado en el historial
    assert 'Estado' in response_content  # Campo modificado
    assert 'Gravedad' in response_content  # Campo modificado
    assert 'pendiente' in response_content.lower()  # Valor anterior
    assert 'en_proceso' in response_content.lower() or 'proceso' in response_content.lower()  # Valor nuevo
    assert 'baja' in response_content.lower()  # Valor anterior gravedad
    assert 'alta' in response_content.lower()  # Valor nuevo gravedad
    
    # Verificar que existe historial registrado
    historial_exists = HistorialCambioIncidente.objects.filter(
        incidente=context.incidente
    ).exists()
    assert historial_exists
