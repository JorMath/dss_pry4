from accounts.models import Usuario
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
import re
import secrets
import string

class AdministratorService:
    
    @staticmethod
    def generar_contrasenia():
        """
        Genera una contraseña temporal segura
        """
        # Generar contraseña de 12 caracteres con letras, números y símbolos
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
        contrasenia = ''.join(secrets.choice(caracteres) for _ in range(12))
        return contrasenia
    
    @staticmethod
    def enviar_correo_credenciales(email, nombre, username, contrasenia_creada, rol):
        """
        Envía un correo con las credenciales de acceso
        """
        asunto = "Credenciales de Acceso - Sistema de Incidentes de Seguridad"
        
        mensaje = f"""
Estimado/a {nombre},

Su cuenta ha sido creada exitosamente en el Sistema de Incidentes de Seguridad.

Credenciales de acceso:
Usuario: {username}
Contraseña: {contrasenia_creada}
Rol asignado: {dict(Usuario.ROL_CHOICES)[rol]}

INSTRUCCIONES IMPORTANTES:
1. Acceda al sistema utilizando las credenciales proporcionadas
2. Mantenga sus credenciales seguras y no las comparta con nadie

Saludos cordiales,
Sistema de Gestión de Incidentes de Seguridad
        """
        
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def crear_usuario(username, email, nombre, rol):
        """
        Crea un usuario con el rol especificado y envía credenciales por correo
        """
        # Validaciones
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya existe")
        
        # Usar el método filter_by_email para verificar email cifrado
        if Usuario.objects.filter_by_email(email).exists():
            raise ValidationError("El email ya está registrado")
        
        # Validar formato de email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Formato de email inválido")
        
        # Validar rol
        roles_validos = ['reportante', 'analista', 'jefe']
        if rol not in roles_validos:
            raise ValidationError("Rol inválido")
        
        try:
            # Generar contraseña temporal
            contrasenia_nueva = AdministratorService.generar_contrasenia()
            
            # Crear usuario usando create_user para manejar el cifrado automáticamente
            usuario = Usuario.objects.create_user(
                username=username,
                email=email,
                password=contrasenia_nueva,
                nombre=nombre,
                rol=rol
            )
            
            # Enviar correo con credenciales
            correo_enviado = AdministratorService.enviar_correo_credenciales(
                email, nombre, username, contrasenia_nueva, rol
            )
            
            # Agregar información del estado del correo al usuario
            usuario.correo_enviado = correo_enviado
            usuario.contraseña_temporal = contrasenia_nueva
            
            return usuario
            
        except Exception as e:
            raise ValidationError(f"Error al crear usuario: {str(e)}")
    
    @staticmethod
    def listar_usuarios():
        """
        Lista todos los usuarios del sistema
        """
        return Usuario.objects.all().order_by('rol', 'username')
    
    @staticmethod
    def obtener_estadisticas():
        """
        Obtiene estadísticas de usuarios
        """
        total_usuarios = Usuario.objects.count()
        jefes = Usuario.objects.filter(rol='jefe').count()
        analistas = Usuario.objects.filter(rol='analista').count()
        reportantes = Usuario.objects.filter(rol='reportante').count()
        
        return {
            'total': total_usuarios,
            'jefes': jefes,
            'analistas': analistas,
            'reportantes': reportantes
        }
    
    @staticmethod
    def actualizar_usuario(usuario_id, **kwargs):
        """
        Actualiza un usuario existente
        """
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            
            for campo, valor in kwargs.items():
                if hasattr(usuario, campo):
                    setattr(usuario, campo, valor)
            
            usuario.save()
            return usuario
            
        except Usuario.DoesNotExist:
            raise ValidationError("Usuario no encontrado")
        except Exception as e:
            raise ValidationError(f"Error al actualizar usuario: {str(e)}")
    
    @staticmethod
    def eliminar_usuario(usuario_id):
        """
        Elimina un usuario (excepto jefes de seguridad)
        """
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            
            if usuario.rol == 'jefe':
                raise ValidationError("No se puede eliminar un jefe de seguridad")
            
            usuario.delete()
            return True
            
        except Usuario.DoesNotExist:
            raise ValidationError("Usuario no encontrado")
        except Exception as e:
            raise ValidationError(f"Error al eliminar usuario: {str(e)}")
    
    @staticmethod
    def restablecer_contrasenia(email):
        """
        Restablece la contraseña de un usuario y envía nueva contraseña por correo
        """
        try:
            # Buscar usuario por email usando el manager personalizado
            usuario = Usuario.objects.get_by_email(email)
            
            # Generar nueva contraseña temporal
            nueva_contrasenia = AdministratorService.generar_contrasenia()
            
            # Actualizar contraseña en la base de datos
            usuario.password = make_password(nueva_contrasenia)
            usuario.save()
            
            # Enviar correo con nueva contraseña usando el email descifrado
            correo_enviado = AdministratorService.enviar_correo_restablecimiento(
                usuario.email_plain, usuario.nombre or usuario.username, nueva_contrasenia
            )
            
            return {
                'success': True,
                'correo_enviado': correo_enviado,
                'usuario': usuario.username
            }
            
        except Usuario.DoesNotExist:
            raise ValidationError("No se encontró ningún usuario con ese correo electrónico")
        except Exception as e:
            raise ValidationError(f"Error al restablecer contraseña: {str(e)}")
    
    @staticmethod
    def enviar_correo_restablecimiento(email, nombre, nueva_contrasenia):
        """
        Envía correo con la nueva contraseña temporal
        """
        asunto = "Restablecimiento de Contraseña - Sistema de Seguridad"
        
        mensaje = f"""
Estimado/a {nombre},

Has solicitado restablecer tu contraseña para el Sistema de Gestión de Incidentes de Seguridad.

Tu nueva contraseña es: {nueva_contrasenia}

INSTRUCCIONES IMPORTANTES:
1. Inicia sesión con tu usuario y esta contraseña
2. Esta contraseña es válida inmediatamente

Si no solicitaste este cambio, contacta inmediatamente al administrador del sistema.

Saludos cordiales,
Sistema de Gestión de Incidentes de Seguridad
        """
        
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log del error en lugar de print
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error enviando correo de restablecimiento: {e}")
            return False