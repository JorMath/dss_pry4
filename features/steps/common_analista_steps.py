from behave import given, when, then
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from incidentes.models import Incidente, HistorialCambioIncidente
from accounts.models import Usuario

User = get_user_model()

@given('que soy un analista de seguridad autenticado en el sistema')
def step_impl(context):
    # Intentar obtener el analista existente o crear uno nuevo
    try:
        context.analista = Usuario.objects.get(username='analista_test')
    except Usuario.DoesNotExist:
        context.analista = Usuario.objects.create_user(
            username='analista_test',
            password='password123',
            nombre='Analista Test',
            rol='analista'
        )
    
    # Configurar cliente y autenticar
    context.client = Client()
    context.client.login(username='analista_test', password='password123')
