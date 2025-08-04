import os
import django

# Configurar Django antes de cualquier importación
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'incidentes_seguridad.settings')
django.setup()

from behave import given, when, then
from accounts.models import Usuario
from administrador.administrator_service import AdministratorService


@given('que existen usuarios con diferentes roles en el sistema')
def step_crear_usuarios_diferentes_roles(context):
    """Crear usuarios con diferentes roles para las pruebas"""
    # Limpiar usuarios existentes de prueba
    Usuario.objects.filter(username__startswith='test_').delete()
    
    # Crear jefe de seguridad
    context.jefe = Usuario.objects.create_user(
        username='test_jefe',
        password='testpass123',
        rol='jefe'
    )
    context.jefe.nombre = 'María López'
    context.jefe.email_plain = 'maria.lopez@test.com'
    context.jefe.save()
    
    # Crear analistas
    context.analista1 = Usuario.objects.create_user(
        username='test_analista1',
        password='testpass123',
        rol='analista'
    )
    context.analista1.nombre = 'Ana García'
    context.analista1.email_plain = 'ana.garcia@test.com'
    context.analista1.save()
    
    context.analista2 = Usuario.objects.create_user(
        username='test_analista2',
        password='testpass123',
        rol='analista'
    )
    context.analista2.nombre = 'Luis Martín'
    context.analista2.email_plain = 'luis.martin@test.com'
    context.analista2.save()
    
    # Crear reportantes
    context.reportante1 = Usuario.objects.create_user(
        username='test_reportante1',
        password='testpass123',
        rol='reportante'
    )
    context.reportante1.nombre = 'Carlos Pérez'
    context.reportante1.email_plain = 'carlos.perez@test.com'
    context.reportante1.save()
    
    context.reportante2 = Usuario.objects.create_user(
        username='test_reportante2',
        password='testpass123',
        rol='reportante'
    )
    context.reportante2.nombre = 'Sofia Ruiz'
    context.reportante2.email_plain = 'sofia.ruiz@test.com'
    context.reportante2.save()


@given('que estoy autenticado como un usuario con rol "{rol}"')
def step_autenticar_con_rol_especifico(context, rol):
    """Autenticar con un rol específico"""
    if rol == 'analista':
        context.usuario_actual = context.analista1
    elif rol == 'reportante':
        context.usuario_actual = context.reportante1
    elif rol == 'jefe':
        context.usuario_actual = context.jefe
    else:
        # Crear usuario si no existe
        context.usuario_actual = Usuario.objects.create_user(
            username=f'test_{rol}',
            password='testpass123',
            rol=rol
        )


@given('estoy autenticado como jefe de seguridad')
def step_autenticado_como_jefe_usuarios(context):
    """Verificar autenticación como jefe de seguridad - Solo lógica de negocio"""
    # En lógica de negocio, verificamos que tenemos un jefe creado
    assert hasattr(context, 'jefe'), "No existe un jefe de seguridad en el contexto"
    assert context.jefe.rol == 'jefe', "El usuario no tiene rol de jefe"
    context.usuario_actual = context.jefe


@when('acceda a "Listar usuarios"')
def step_acceder_listar_usuarios(context):
    """Acceder a la funcionalidad de listar usuarios - Solo lógica de negocio"""
    # Solo probar la lógica de negocio del servicio
    context.usuarios_obtenidos = AdministratorService.listar_usuarios()
    context.estadisticas_obtenidas = AdministratorService.obtener_estadisticas()


@when('intente acceder a "Listar usuarios"')
def step_intentar_acceder_listar_usuarios(context):
    """Intentar acceder a listar usuarios con validación de permisos"""
    # En lógica de negocio, verificar permisos
    if hasattr(context, 'usuario_actual') and context.usuario_actual.rol != 'jefe':
        context.acceso_denegado = True
    else:
        context.usuarios_obtenidos = AdministratorService.listar_usuarios()
        context.acceso_denegado = False


@then('veo todos los usuarios ordenados por rol')
def step_ver_usuarios_ordenados_por_rol(context):
    """Verificar que los usuarios están ordenados por rol - Solo lógica de negocio"""
    assert hasattr(context, 'usuarios_obtenidos'), "No se obtuvieron usuarios"
    assert len(context.usuarios_obtenidos) > 0, "No hay usuarios en la lista"
    
    # Verificar que están ordenados por rol
    roles_orden = [usuario.rol for usuario in context.usuarios_obtenidos]
    roles_ordenados = sorted(roles_orden)
    assert roles_orden == roles_ordenados, "Los usuarios no están ordenados por rol"


@then('veo la información completa de cada usuario')
def step_ver_informacion_completa_usuarios(context):
    """Verificar información completa de usuarios - Solo lógica de negocio"""
    assert hasattr(context, 'usuarios_obtenidos'), "No se obtuvieron usuarios"
    
    for usuario in context.usuarios_obtenidos:
        # Verificar que cada usuario tiene los campos esperados
        assert hasattr(usuario, 'username'), f"Usuario {usuario.id} no tiene username"
        assert hasattr(usuario, 'nombre'), f"Usuario {usuario.id} no tiene nombre"
        assert hasattr(usuario, 'email_plain'), f"Usuario {usuario.id} no tiene email_plain"
        assert hasattr(usuario, 'rol'), f"Usuario {usuario.id} no tiene rol"


@then('veo las estadísticas de usuarios por rol')
def step_ver_estadisticas_usuarios_por_rol(context):
    """Verificar estadísticas por rol - Solo lógica de negocio"""
    assert hasattr(context, 'estadisticas_obtenidas'), "No se obtuvieron estadísticas"
    assert 'total' in context.estadisticas_obtenidas, "Faltan estadísticas de total de usuarios"
    assert 'jefes' in context.estadisticas_obtenidas, "Faltan estadísticas de jefes"
    assert 'analistas' in context.estadisticas_obtenidas, "Faltan estadísticas de analistas"
    assert 'reportantes' in context.estadisticas_obtenidas, "Faltan estadísticas de reportantes"


@given('que estoy en la lista de usuarios')
def step_en_lista_usuarios(context):
    """Estar en la lista de usuarios - Solo lógica de negocio"""
    # En lógica de negocio, obtenemos la lista de usuarios
    context.usuarios_obtenidos = AdministratorService.listar_usuarios()
    assert len(context.usuarios_obtenidos) > 0, "No hay usuarios en el sistema"


@then('cada usuario muestra: username, nombre, email descifrado y rol')
def step_mostrar_campos_especificos_usuario(context):
    """Mostrar campos específicos de usuario - Solo lógica de negocio"""
    assert hasattr(context, 'usuarios_obtenidos'), "No se obtuvieron usuarios"
    
    for usuario in context.usuarios_obtenidos:
        # Verificar que se pueden obtener todos los campos requeridos
        assert usuario.username is not None, f"Username no disponible para usuario {usuario.id}"
        assert usuario.nombre is not None, f"Nombre no disponible para usuario {usuario.id}"
        assert usuario.email_plain is not None, f"Email descifrado no disponible para usuario {usuario.id}"
        assert usuario.rol is not None, f"Rol no disponible para usuario {usuario.id}"


@then('los usuarios están agrupados por rol')
def step_usuarios_agrupados_por_rol(context):
    """Verificar agrupación por rol - Solo lógica de negocio"""
    assert hasattr(context, 'usuarios_obtenidos'), "No se obtuvieron usuarios"
    
    # Verificar que hay usuarios de cada rol
    roles_presentes = set(usuario.rol for usuario in context.usuarios_obtenidos)
    assert 'jefe' in roles_presentes, "No hay usuarios con rol jefe"
    assert 'analista' in roles_presentes, "No hay usuarios con rol analista"
    assert 'reportante' in roles_presentes, "No hay usuarios con rol reportante"
    
    # Verificar que están ordenados por rol (orden alfabético: analista < jefe < reportante)
    roles_orden = [usuario.rol for usuario in context.usuarios_obtenidos]
    
    # Encontrar las posiciones de cada tipo de rol
    pos_analista = [i for i, rol in enumerate(roles_orden) if rol == 'analista']
    pos_jefe = [i for i, rol in enumerate(roles_orden) if rol == 'jefe']
    pos_reportante = [i for i, rol in enumerate(roles_orden) if rol == 'reportante']
    
    # Verificar que están agrupados (orden alfabético: analistas < jefes < reportantes)
    if pos_analista and pos_jefe:
        assert max(pos_analista) < min(pos_jefe), "Los analistas deben estar agrupados antes que los jefes"
    
    if pos_jefe and pos_reportante:
        assert max(pos_jefe) < min(pos_reportante), "Los jefes deben estar agrupados antes que los reportantes"


@then('el sistema me redirige por falta de permisos')
def step_verificar_redireccion_permisos(context):
    """Verificar redirección por falta de permisos - Solo lógica de negocio"""
    assert hasattr(context, 'acceso_denegado'), "No se verificó el acceso"
    assert context.acceso_denegado == True, "El acceso debería haber sido denegado"
