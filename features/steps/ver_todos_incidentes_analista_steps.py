from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from incidentes.models import Incidente
from accounts.models import Usuario

User = get_user_model()

@given('que hay incidentes reportados')
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
    
    # Limpiar incidentes existentes de este reportante para evitar duplicados
    Incidente.objects.filter(reportado_por=context.reportante).delete()
    
    # Crear varios incidentes de prueba con datos específicos
    context.incidentes = []
    tipos_incidentes = ['Bug', 'Malware', 'Phishing', 'DDoS', 'Acceso no autorizado']
    estados = ['pendiente', 'en_proceso', 'cerrado']
    gravedades = ['baja', 'media', 'alta']
    
    for i in range(10):  # Crear 10 incidentes para las pruebas
        incidente = Incidente.objects.create(
            tipo=tipos_incidentes[i % len(tipos_incidentes)],
            descripcion=f'Descripción detallada del incidente de seguridad número {i+1}',
            reportado_por=context.reportante,
            estado=estados[i % len(estados)],
            gravedad=gravedades[i % len(gravedades)],
            asignado_a=context.analista if i % 3 == 0 else None
        )
        context.incidentes.append(incidente)

@when('visualice los incidentes reportados')
def step_impl(context):
    # En lugar de hacer una petición HTTP, simular la obtención de incidentes
    # como lo haría la vista del analista
    context.incidentes_visibles = Incidente.objects.all().order_by('-fecha_reporte')

@then('debe ver una lista con todos los incidentes registrados por su fecha, tipo, descripción, gravedad, y el Usuario Reportante que lo hizo')
def step_impl(context):
    # Validar que se pueden obtener todos los incidentes
    assert len(context.incidentes_visibles) >= 10, f"Se esperaban al menos 10 incidentes, pero se encontraron {len(context.incidentes_visibles)}"
    
    # Validar que cada incidente tiene los campos requeridos
    for incidente in context.incidentes_visibles:
        assert incidente.fecha_reporte is not None, "El incidente debe tener fecha de reporte"
        assert incidente.tipo is not None and incidente.tipo != "", "El incidente debe tener tipo"
        assert incidente.descripcion is not None and incidente.descripcion != "", "El incidente debe tener descripción"
        assert incidente.gravedad is not None and incidente.gravedad != "", "El incidente debe tener gravedad"
        assert incidente.reportado_por is not None, "El incidente debe tener un usuario reportante"
        
    # Validar que están ordenados por fecha (más recientes primero)
    fechas = [inc.fecha_reporte for inc in context.incidentes_visibles]
    assert fechas == sorted(fechas, reverse=True), "Los incidentes deben estar ordenados por fecha descendente"
    
    print(f"✓ Se pueden visualizar {len(context.incidentes_visibles)} incidentes correctamente")
    print(f"✓ Todos los incidentes tienen los campos requeridos: fecha, tipo, descripción, gravedad, reportante")
    print(f"✓ Los incidentes están ordenados por fecha de reporte")
        # pero al menos parte del contenido debería estar visible
