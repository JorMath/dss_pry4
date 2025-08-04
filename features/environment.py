import os
import django

def before_all(context):
    """Configuración inicial antes de todas las pruebas"""
    # Configurar Django si no está configurado
    if not hasattr(django.conf.settings, 'configured') or not django.conf.settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
        django.setup()
    
    # Configurar las bases de datos para los tests de Behave
    from behave_django.testcase import BehaviorDrivenTestCase
    BehaviorDrivenTestCase.databases = ['default', 'logs']

def after_all(context):
    """Limpieza después de todas las pruebas"""
    pass

def before_scenario(context, scenario):
    """Configuración antes de cada escenario"""
    # Limpiar datos de prueba antes de cada escenario
    try:
        from accounts.models import Usuario
        from incidentes.models import Incidente, HistorialCambioIncidente
        
        # Limpiar usuarios de prueba específicos
        Usuario.objects.filter(username__in=[
            'analista_test', 'reportante_test', 'juan',
            'analista1_test', 'analista2_test', 'test_reportante'
        ]).delete()
        
        # Limpiar incidentes de prueba
        Incidente.objects.filter(descripcion__icontains='test').delete()
        Incidente.objects.filter(descripcion__icontains='prueba').delete()
        Incidente.objects.filter(descripcion__icontains='incidente de seguridad número').delete()
        
        # Limpiar historial
        HistorialCambioIncidente.objects.all().delete()
        
    except Exception:
        # No fallar si hay problemas con la limpieza
        pass

def after_scenario(context, _):
    """Limpieza después de cada escenario"""
    # Limpiar datos de prueba después de cada escenario
    try:
        from accounts.models import Usuario
        from incidentes.models import Incidente, HistorialCambioIncidente
        
        # Limpiar usuarios de prueba específicos
        Usuario.objects.filter(username__in=[
            'analista_test', 'reportante_test', 'juan',
            'analista1_test', 'analista2_test', 'test_reportante'
        ]).delete()
        
        # Limpiar incidentes de prueba
        Incidente.objects.filter(descripcion__icontains='test').delete()
        Incidente.objects.filter(descripcion__icontains='prueba').delete()
        Incidente.objects.filter(descripcion__icontains='incidente de seguridad número').delete()
        
        # Limpiar historial
        HistorialCambioIncidente.objects.all().delete()
        
    except Exception:
        # No fallar si hay problemas con la limpieza
        pass
