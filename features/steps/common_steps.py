import os
import django

# Configurar Django antes de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
django.setup()

from behave import given
from django.test import Client
from accounts.models import Usuario


@given('que soy un usuario reportante autenticado')
def step_dado_usuario_reportante(context):
    # Limpiar datos de prueba previos
    Usuario.objects.filter(username='test_reportante').delete()
    
    # Crear usuario reportante de prueba
    context.usuario_reportante = Usuario.objects.create_user(
        username='test_reportante',
        email='reportante@test.com',
        password='password123',
        rol='reportante',
        nombre='Usuario Reportante Test'
    )
    context.client = Client()
    context.client.force_login(context.usuario_reportante)
