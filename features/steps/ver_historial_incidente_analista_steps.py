from behave import given, when, then
from django.contrib.auth import get_user_model
from incidentes.models import Incidente, HistorialCambioIncidente
from accounts.models import Usuario
from datetime import datetime, timezone

User = get_user_model()

@given('que existe un incidente con historial de cambios por múltiples analistas')
def step_impl(context):
    # Crear analista1
    try:
        context.analista1 = Usuario.objects.get(username='analista1_test')
    except Usuario.DoesNotExist:
        context.analista1 = Usuario.objects.create_user(
            username='analista1_test',
            password='password123',
            nombre='Analista Uno',
            rol='analista'
        )
    
    # Crear analista2
    try:
        context.analista2 = Usuario.objects.get(username='analista2_test')
    except Usuario.DoesNotExist:
        context.analista2 = Usuario.objects.create_user(
            username='analista2_test',
            password='password123',
            nombre='Analista Dos',
            rol='analista'
        )
    
    # Usar el incidente ya existente del contexto
    # Crear historial de cambios simulando múltiples modificaciones
    cambios = [
        {
            'usuario_modificacion': context.analista1,
            'campo_modificado': 'estado',
            'valor_anterior': 'pendiente',
            'valor_nuevo': 'en_proceso',
            'descripcion': 'Iniciando análisis del incidente'
        },
        {
            'usuario_modificacion': context.analista1,
            'campo_modificado': 'gravedad',
            'valor_anterior': 'media',
            'valor_nuevo': 'alta',
            'descripcion': 'Incrementando gravedad tras análisis inicial'
        },
        {
            'usuario_modificacion': context.analista2,
            'campo_modificado': 'asignado_a',
            'valor_anterior': str(context.analista1.id),
            'valor_nuevo': str(context.analista2.id),
            'descripcion': 'Reasignando incidente para análisis especializado'
        },
        {
            'usuario_modificacion': context.analista2,
            'campo_modificado': 'estado',
            'valor_anterior': 'en_proceso',
            'valor_nuevo': 'cerrado',
            'descripcion': 'Incidente resuelto después de análisis completo'
        }
    ]
    
    context.cambios_historial = []
    for cambio in cambios:
        historial = HistorialCambioIncidente.objects.create(
            incidente=context.incidente,
            **cambio
        )
        context.cambios_historial.append(historial)

@when('consulte el historial de cambios del incidente')
def step_impl(context):
    # Simular la obtención del historial como lo haría la vista
    context.historial_consulta = HistorialCambioIncidente.objects.filter(
        incidente=context.incidente
    ).order_by('-fecha_cambio')

@then('debe ver todos los cambios realizados ordenados cronológicamente con usuario, fecha, campo modificado y valores anterior y nuevo')
def step_impl(context):
    # Validar que se recuperó todo el historial
    assert len(context.historial_consulta) >= 4, f"Se esperaban al menos 4 cambios en el historial, pero se encontraron {len(context.historial_consulta)}"
    
    # Validar que cada entrada del historial tiene la información requerida
    for cambio in context.historial_consulta:
        assert cambio.usuario_modificacion is not None, "Cada cambio debe tener un usuario que lo modificó"
        assert cambio.fecha_cambio is not None, "Cada cambio debe tener fecha"
        assert cambio.campo_modificado is not None and cambio.campo_modificado != "", "Cada cambio debe especificar el campo modificado"
        assert cambio.valor_anterior is not None, "Cada cambio debe tener el valor anterior"
        assert cambio.valor_nuevo is not None, "Cada cambio debe tener el valor nuevo"
    
    # Validar que están ordenados cronológicamente (más recientes primero)
    fechas = [cambio.fecha_cambio for cambio in context.historial_consulta]
    assert fechas == sorted(fechas, reverse=True), "Los cambios deben estar ordenados cronológicamente (más recientes primero)"
    
    # Validar que se incluyen cambios de múltiples analistas
    usuarios_modificadores = set(cambio.usuario_modificacion.id for cambio in context.historial_consulta)
    assert len(usuarios_modificadores) >= 2, "El historial debe incluir cambios de múltiples analistas"
    
    # Validar que se incluyen diferentes tipos de cambios
    campos_modificados = set(cambio.campo_modificado for cambio in context.historial_consulta)
    campos_esperados = {'estado', 'gravedad', 'asignado_a'}
    assert campos_esperados.issubset(campos_modificados), f"El historial debe incluir cambios en campos: {campos_esperados}"
    
    print(f"✓ Se consultó el historial completo con {len(context.historial_consulta)} cambios")
    print(f"✓ Todos los cambios incluyen: usuario, fecha, campo modificado, valores anterior y nuevo")
    print(f"✓ Los cambios están ordenados cronológicamente")
    print(f"✓ El historial incluye cambios de {len(usuarios_modificadores)} analistas diferentes")
    print(f"✓ Se registraron cambios en los campos: {', '.join(campos_modificados)}")
