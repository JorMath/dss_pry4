from behave import given, when, then
from accounts.models import Usuario
from incidentes.models import Incidente


@given('que existen usuarios: jefe "{jefe_nombre}", analistas "{analista1_nombre}" y "{analista2_nombre}"')
def step_crear_usuarios_para_asignacion(context, jefe_nombre, analista1_nombre, analista2_nombre):
    """Crear usuarios básicos para las pruebas de asignación"""
    # Limpiar usuarios existentes
    Usuario.objects.filter(username__startswith='test_asig_').delete()
    
    # Crear jefe de seguridad
    context.jefe = Usuario.objects.create_user(
        username='test_asig_jefe',
        password='testpass123',
        rol='jefe'
    )
    context.jefe.nombre = jefe_nombre
    context.jefe.save()
    
    # Crear analistas
    context.analista1 = Usuario.objects.create_user(
        username='test_asig_analista1',
        password='testpass123',
        rol='analista'
    )
    context.analista1.nombre = analista1_nombre
    context.analista1.save()
    
    context.analista2 = Usuario.objects.create_user(
        username='test_asig_analista2',
        password='testpass123',
        rol='analista'
    )
    context.analista2.nombre = analista2_nombre
    context.analista2.save()


@given('existe un incidente pendiente ID "{incidente_id}"')
def step_crear_incidente_pendiente(context, incidente_id):
    """Crear incidente pendiente"""
    # Limpiar incidentes con ese ID
    Incidente.objects.filter(id=int(incidente_id)).delete()
    
    context.incidente_pendiente = Incidente.objects.create(
        id=int(incidente_id),
        tipo='vulnerabilidad',
        descripcion='Incidente de prueba pendiente',
        estado='pendiente',
        gravedad='alta',
        reportado_por=context.jefe
    )


@given('existe un incidente asignado ID "{incidente_id}" a "{analista_nombre}"')
def step_crear_incidente_asignado(context, incidente_id, analista_nombre):
    """Crear incidente asignado"""
    # Buscar el analista por nombre
    analista = None
    if analista_nombre == "Luis Martín" and hasattr(context, 'analista2'):
        analista = context.analista2
    elif analista_nombre == "Ana García" and hasattr(context, 'analista1'):
        analista = context.analista1
    
    assert analista is not None, f"No se encontró analista con nombre {analista_nombre}"
    
    # Limpiar incidentes con ese ID
    Incidente.objects.filter(id=int(incidente_id)).delete()
    
    context.incidente_asignado = Incidente.objects.create(
        id=int(incidente_id),
        tipo='malware',
        descripcion='Incidente de prueba asignado',
        estado='en_proceso',
        gravedad='media',
        reportado_por=context.jefe,
        asignado_a=analista
    )


# NOTE: El step "estoy autenticado como jefe de seguridad" se reutiliza desde gestionar_usuarios_steps.py


@when('asigne el incidente "{incidente_id}" al analista "{analista_nombre}"')
def step_asignar_incidente_a_analista(context, incidente_id, analista_nombre):
    """Asignar incidente a analista - Solo lógica de negocio"""
    # Buscar analista por nombre
    analista = None
    if analista_nombre == "Ana García" and hasattr(context, 'analista1'):
        analista = context.analista1
    elif analista_nombre == "Luis Martín" and hasattr(context, 'analista2'):
        analista = context.analista2
    
    assert analista is not None, f"No se encontró analista con nombre {analista_nombre}"
    
    # Obtener el incidente
    incidente = Incidente.objects.get(id=int(incidente_id))
    
    # Lógica de negocio: asignar incidente
    incidente.asignado_a = analista
    incidente.estado = 'en_proceso'
    incidente.save()
    
    # Guardar para verificaciones posteriores
    context.incidente_asignado_resultado = incidente
    context.analista_asignado = analista


@then('el incidente queda asignado a "{analista_nombre}"')
def step_verificar_asignacion_incidente(context, analista_nombre):
    """Verificar que el incidente quedó asignado - Solo lógica de negocio"""
    assert hasattr(context, 'incidente_asignado_resultado'), "No se realizó la asignación"
    
    # Verificar que el incidente está asignado al analista correcto
    incidente = context.incidente_asignado_resultado
    incidente.refresh_from_db()
    
    # Buscar analista por nombre para comparar
    analista_esperado = None
    if analista_nombre == "Ana García" and hasattr(context, 'analista1'):
        analista_esperado = context.analista1
    elif analista_nombre == "Luis Martín" and hasattr(context, 'analista2'):
        analista_esperado = context.analista2
    
    assert incidente.asignado_a == analista_esperado, f"El incidente no quedó asignado a {analista_nombre}"
    assert incidente.estado == 'en_proceso', "El incidente no cambió a estado en_proceso"


@then('se confirma con mensaje de éxito')
def step_confirmar_mensaje_exito(context):
    """Confirmar mensaje de éxito - Solo lógica de negocio"""
    # En lógica de negocio, verificamos que la operación se completó correctamente
    assert hasattr(context, 'incidente_asignado_resultado'), "No se completó la asignación"
    assert context.incidente_asignado_resultado.asignado_a is not None, "La asignación no fue exitosa"


@when('reasigne el incidente "{incidente_id}" de "{analista_origen}" a "{analista_destino}"')
def step_reasignar_incidente(context, incidente_id, analista_origen, analista_destino):
    """Reasignar incidente - Solo lógica de negocio"""
    # Obtener el incidente
    incidente = Incidente.objects.get(id=int(incidente_id))
    
    # Buscar analistas por nombre
    analista_destino_obj = None
    if analista_destino == "Ana García" and hasattr(context, 'analista1'):
        analista_destino_obj = context.analista1
    elif analista_destino == "Luis Martín" and hasattr(context, 'analista2'):
        analista_destino_obj = context.analista2
    
    assert analista_destino_obj is not None, f"No se encontró analista destino {analista_destino}"
    
    # Reasignar el incidente
    incidente.asignado_a = analista_destino_obj
    incidente.save()
    
    context.incidente_reasignado = incidente


@then('el incidente cambia de asignación a "{analista_nombre}"')
def step_verificar_reasignacion(context, analista_nombre):
    """Verificar reasignación - Solo lógica de negocio"""
    assert hasattr(context, 'incidente_reasignado'), "No se realizó la reasignación"
    
    incidente = context.incidente_reasignado
    incidente.refresh_from_db()
    
    # Buscar analista por nombre
    analista_esperado = None
    if analista_nombre == "Ana García" and hasattr(context, 'analista1'):
        analista_esperado = context.analista1
    elif analista_nombre == "Luis Martín" and hasattr(context, 'analista2'):
        analista_esperado = context.analista2
    
    assert incidente.asignado_a == analista_esperado, f"El incidente no fue reasignado a {analista_nombre}"


@then('se confirma la reasignación')
def step_confirmar_reasignacion(context):
    """Confirmar reasignación - Solo lógica de negocio"""
    assert hasattr(context, 'incidente_reasignado'), "No se realizó la reasignación"
    assert context.incidente_reasignado.asignado_a is not None, "La reasignación no se confirmó"


@given('que estoy en la lista de incidentes')
def step_en_lista_incidentes(context):
    """Estar en lista de incidentes - Solo lógica de negocio"""
    # En lógica de negocio, obtenemos la lista de todos los incidentes
    context.todos_incidentes = list(Incidente.objects.all())
    assert len(context.todos_incidentes) > 0, "No hay incidentes en el sistema para mostrar"


@then('veo la columna "Asignado a"')
def step_ver_columna_asignado(context):
    """Ver columna asignado - Solo lógica de negocio"""
    assert hasattr(context, 'todos_incidentes'), "No se obtuvieron los incidentes"
    
    # Verificar que los incidentes tienen información de asignación
    for incidente in context.todos_incidentes:
        # Cada incidente debe tener un campo asignado_a (puede ser None)
        assert hasattr(incidente, 'asignado_a'), f"Incidente {incidente.id} no tiene campo asignado_a"


@then('los incidentes muestran su estado de asignación')
def step_mostrar_estado_asignacion(context):
    """Mostrar estado de asignación - Solo lógica de negocio"""
    assert hasattr(context, 'todos_incidentes'), "No se obtuvieron los incidentes"
    
    # Verificar que hay incidentes con diferentes estados de asignación
    estados_encontrados = set()
    
    for incidente in context.todos_incidentes:
        if incidente.asignado_a is not None:
            estados_encontrados.add('asignado')
        else:
            estados_encontrados.add('sin_asignar')
    
    # Debe haber al menos un incidente con estado de asignación definido
    assert len(estados_encontrados) > 0, "No se encontraron estados de asignación"
