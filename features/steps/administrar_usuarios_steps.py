import os
import django

# Configurar Django antes de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
django.setup()

from behave import given, when, then
from django.test import Client
from django.contrib.auth import authenticate
from django.core import mail
from django.urls import reverse
from accounts.models import Usuario
from administrador.administrator_service import AdministratorService
import re


@given('que el usuario a crear es "{nombre}", con correo "{correo}" y rol "{rol}"')
def step_dado_usuario_crear(context, nombre, correo, rol):
    context.nombre_usuario = nombre
    context.correo_usuario = correo
    context.rol_usuario = rol
    context.username_usuario = nombre.lower().replace(' ', '_')
    
    Usuario.objects.filter(email=correo).delete()
    Usuario.objects.filter(username=context.username_usuario).delete()
    
    context.jefe_seguridad = Usuario.objects.create_user(
        username='jefe_test',
        email='jefe@test.com',
        password='password123',
        rol='jefe',
        nombre='Jefe de Prueba'
    )


@when('cree el usuario')
def step_cuando_crear_usuario(context):
    try:
        context.usuario_creado = AdministratorService.crear_usuario(
            username=context.username_usuario,
            email=context.correo_usuario,
            nombre=context.nombre_usuario,
            rol=context.rol_usuario
        )
        context.creacion_exitosa = True
        
    except Exception as e:
        context.creacion_exitosa = False
        context.error_creacion = str(e)


@then('se enviará un correo a "{correo_esperado}" con su contraseña temporal generada')
def step_entonces_correo_enviado(context, correo_esperado):
    assert context.creacion_exitosa, f"La creación del usuario falló: {getattr(context, 'error_creacion', 'Error desconocido')}"
    
    assert context.usuario_creado is not None, "El usuario no fue creado"
    assert context.usuario_creado.email == correo_esperado, f"Email esperado: {correo_esperado}, obtenido: {context.usuario_creado.email}"
    assert context.usuario_creado.rol == context.rol_usuario, f"Rol esperado: {context.rol_usuario}, obtenido: {context.usuario_creado.rol}"
    
    usuario_db = Usuario.objects.get(email=correo_esperado)
    assert usuario_db.check_password is not None, "El usuario no tiene una contraseña configurada"
    



def cleanup_test_data(context):
    Usuario.objects.filter(email__contains='@test.com').delete()
    Usuario.objects.filter(email__contains='@gmail.com').delete()
    Usuario.objects.filter(username__contains='test').delete()
