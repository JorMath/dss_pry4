import os
import django

def before_all(context):
    """Configuración inicial antes de todas las pruebas"""
    # Configurar Django si no está configurado
    if not hasattr(django.conf.settings, 'configured') or not django.conf.settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
        django.setup()

def after_all(context):
    """Limpieza después de todas las pruebas"""
    pass

def before_scenario(context, scenario):
    """Configuración antes de cada escenario"""
    pass

def after_scenario(context, _):
    """Limpieza después de cada escenario"""
    # Limpiar datos de prueba con compatibilidad para campos cifrados
    try:
        from accounts.models import Usuario
        from incidentes.models import Incidente
        
        # Limpiar usuarios de prueba (usar métodos que funcionen con cifrado)
        usuarios_test = Usuario.objects.filter(username__contains='test')
        for usuario in usuarios_test:
            if usuario.email_plain and '@test.com' in usuario.email_plain:
                usuario.delete()
        
        # También limpiar por username de prueba
        Usuario.objects.filter(username__in=['jorman_test', 'reportante_test', 'analista_test']).delete()
        
        # Limpiar incidentes de prueba
        Incidente.objects.filter(descripcion__icontains='test').delete()
        Incidente.objects.filter(descripcion__icontains='bug permite escribir').delete()
        
    except Exception:
        # No fallar si hay problemas con la limpieza
        pass
