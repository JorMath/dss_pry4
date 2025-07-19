import os
import django
from django.core import mail
from django.conf import settings


def before_all(context):
    if not hasattr(django.conf.settings, 'configured') or not django.conf.settings.configured:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
        django.setup()
    
    # Forzar backend SMTP real para las pruebas
    settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


def after_all(context):
    pass


def before_scenario(context, scenario):
    from accounts.models import Usuario
    from django.core import mail
    from django.conf import settings
    
    Usuario.objects.filter(email__contains='test').delete()
    Usuario.objects.filter(email__contains='gmail.com').delete()
    Usuario.objects.filter(username__contains='test').delete()
    
    # Solo limpiar outbox si estamos usando el backend de memoria
    if hasattr(mail, 'outbox') and settings.EMAIL_BACKEND == 'django.core.mail.backends.locmem.EmailBackend':
        mail.outbox.clear()


def after_scenario(context, scenario):
    try:
        from features.steps.administrar_usuarios_steps import cleanup_test_data
        cleanup_test_data(context)
    except ImportError:
        pass
