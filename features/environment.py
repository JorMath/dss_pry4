import os
import django

def before_all(context):
    """Configuración inicial antes de todas las pruebas"""
    pass

def after_all(context):
    """Limpieza después de todas las pruebas"""
    pass

def before_scenario(context, scenario):
    """Configuración antes de cada escenario"""
    pass

def after_scenario(context, scenario):
    """Limpieza después de cada escenario"""
    # Limpiar datos de prueba
    try:
        from accounts.models import Usuario
        from incidentes.models import Incidente
        
        # Limpiar datos de prueba
        Usuario.objects.filter(email__contains='@test.com').delete()
        Incidente.objects.filter(reportado_por__email__contains='@test.com').delete()
    except:
        pass
