from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from incidentes.models import Incidente, HistorialCambioIncidente
from accounts.models import Usuario

User = get_user_model()

@given('existe un incidente reportado en estado "{estado}"')
def step_impl(context, estado):
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
    
    # Crear el incidente en estado pendiente
    context.incidente = Incidente.objects.create(
        tipo='bug_seguridad',
        descripcion='Incidente de prueba para clasificación',
        reportado_por=context.reportante,
        estado=estado.lower(),
        gravedad='media'
    )

# Step específico para el escenario del usuario
@given('que hay un incidente reportado en gravedad "{gravedad_inicial}" con el analista "{nombre_analista}"')
def step_impl(context, gravedad_inicial, nombre_analista):
    # Crear o obtener el analista Juan
    try:
        context.analista_juan = Usuario.objects.get(username='juan')
    except Usuario.DoesNotExist:
        context.analista_juan = Usuario.objects.create_user(
            username='juan',
            password='password123',
            nombre=nombre_analista,
            rol='analista'
        )
    
    # Actualizar el incidente existente con la gravedad inicial y asignar al analista
    context.incidente.gravedad = gravedad_inicial.lower()
    context.incidente.asignado_a = context.analista_juan
    context.incidente.save()
    
    # Guardar estado inicial para validaciones posteriores
    context.gravedad_inicial = gravedad_inicial.lower()
    context.estado_inicial = context.incidente.estado
    context.fecha_modificacion_inicial = context.incidente.fecha_actualizacion

@when('el analista "{nombre_analista}" cambie el tipo de gravedad a "{nueva_gravedad}"')
def step_impl(context, nombre_analista, nueva_gravedad):
    # Simular la actualización del incidente como lo haría la vista del analista
    context.incidente.gravedad = nueva_gravedad.lower()
    context.incidente.save()
    
    # Crear registro en el historial de cambios
    HistorialCambioIncidente.objects.create(
        incidente=context.incidente,
        usuario_modificacion=context.analista_juan,
        campo_modificado='gravedad',
        valor_anterior=context.gravedad_inicial,
        valor_nuevo=nueva_gravedad.lower(),
        descripcion=f'Gravedad cambiada de {context.gravedad_inicial} a {nueva_gravedad.lower()}'
    )
    
    context.nueva_gravedad = nueva_gravedad.lower()

@then('el incidente tendrá la gravedad a "{gravedad_esperada}" Y se actualizará la última modificación por "{nombre_analista}"')
def step_impl(context, gravedad_esperada, nombre_analista):
    # Recargar el incidente desde la base de datos
    context.incidente.refresh_from_db()
    
    # Validar que la gravedad cambió correctamente
    assert context.incidente.gravedad == gravedad_esperada.lower(), f"Se esperaba gravedad '{gravedad_esperada.lower()}', pero se encontró '{context.incidente.gravedad}'"
    
    # Validar que se actualizó la fecha de modificación
    assert context.incidente.fecha_actualizacion > context.fecha_modificacion_inicial, "La fecha de actualización debe haberse actualizado"
    
    # Validar que se creó un registro en el historial
    historial = HistorialCambioIncidente.objects.filter(
        incidente=context.incidente,
        usuario_modificacion=context.analista_juan,
        campo_modificado='gravedad'
    ).first()
    
    assert historial is not None, "Se debe crear un registro en el historial de cambios"
    assert historial.valor_anterior == context.gravedad_inicial, f"El valor anterior debe ser '{context.gravedad_inicial}'"
    assert historial.valor_nuevo == gravedad_esperada.lower(), f"El valor nuevo debe ser '{gravedad_esperada.lower()}'"
    
    print(f"✓ La gravedad del incidente cambió correctamente de '{context.gravedad_inicial}' a '{gravedad_esperada.lower()}'")
    print(f"✓ Se actualizó la fecha de modificación del incidente")
    print(f"✓ Se creó el registro en el historial de cambios por el analista '{nombre_analista}'")
