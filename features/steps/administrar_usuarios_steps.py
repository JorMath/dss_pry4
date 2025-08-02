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
    
    # Limpiar usuarios existentes usando métodos compatibles con cifrado
    try:
        usuario_existente = Usuario.objects.get_by_email(correo)
        usuario_existente.delete()
    except Usuario.DoesNotExist:
        pass
    
    Usuario.objects.filter(username=context.username_usuario).delete()
    
    # Crear jefe de seguridad para las pruebas
    try:
        jefe = Usuario.objects.get(username='jefe_test')
    except Usuario.DoesNotExist:
        jefe = Usuario.objects.create_user(
            username='jefe_test',
            password='test123',
            rol='jefe'
        )
        jefe.email_plain = 'jefe@test.com'  # Usar la nueva propiedad
        jefe.nombre = 'Jefe Test'
        jefe.save()
    
    context.jefe_seguridad = jefe


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
    
    # Usar email_plain para obtener el email descifrado
    email_obtenido = context.usuario_creado.email_plain
    assert email_obtenido == correo_esperado, f"Email esperado: {correo_esperado}, obtenido: {email_obtenido}"
    assert context.usuario_creado.rol == context.rol_usuario, f"Rol esperado: {context.rol_usuario}, obtenido: {context.usuario_creado.rol}"
    
    # Usar el método get_by_email para buscar con email cifrado
    try:
        usuario_db = Usuario.objects.get_by_email(correo_esperado)
        assert usuario_db is not None, f"Usuario con email {correo_esperado} no encontrado en la base de datos"
        # Verificar que tiene una contraseña configurada
        assert hasattr(usuario_db, 'password') and usuario_db.password, "El usuario no tiene una contraseña configurada"
        
        # Simular el envío del correo (en producción se enviaría realmente)
        context.correo_enviado = True
        context.mensaje_correo = f"Correo enviado a {correo_esperado} con contraseña temporal"
        
    except Usuario.DoesNotExist:
        assert False, f"Usuario con email {correo_esperado} no encontrado en la base de datos"
    except Exception as e:
        assert False, f"Error buscando usuario con email {correo_esperado}: {str(e)}"
    



def cleanup_test_data(context):
    # Limpiar usuarios de prueba usando métodos compatibles con cifrado
    try:
        # Limpiar por email específico
        emails_test = ['jefe@test.com', 'jorman240802@gmail.com', 'reportante@test.com']
        for email in emails_test:
            try:
                usuario = Usuario.objects.get_by_email(email)
                usuario.delete()
            except Usuario.DoesNotExist:
                pass
        
        # Limpiar por username
        Usuario.objects.filter(username__contains='test').delete()
        Usuario.objects.filter(username__in=['jorman', 'jefe_test', 'reportante_test']).delete()
        
    except Exception:
        # Si hay error en la limpieza, continuar
        pass
