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
    def generar_contraseña_temporal():
        """
        Genera una contraseña temporal segura
        """
        # Generar contraseña de 12 caracteres con letras, números y símbolos
        caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
        contraseña = ''.join(secrets.choice(caracteres) for _ in range(12))
        return contraseña
    
    @staticmethod
    def enviar_correo_credenciales(email, nombre, username, contraseña_temporal, rol):
        """
        Envía un correo con las credenciales de acceso
        """
        asunto = "Credenciales de Acceso - Sistema de Incidentes de Seguridad"
        
        mensaje = f"""
Estimado/a {nombre},

Su cuenta ha sido creada exitosamente en el Sistema de Incidentes de Seguridad.

Credenciales de acceso:
Usuario: {username}
Contraseña: {contraseña_temporal}
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
        except Exception as e:
            return False
    
    @staticmethod
    def crear_usuario(username, email, nombre, rol):
        """
        Crea un usuario con el rol especificado y envía credenciales por correo
        """
        # Validaciones
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya existe")
        
        if Usuario.objects.filter(email=email).exists():
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
            contraseña_temporal = AdministratorService.generar_contraseña_temporal()
            
            # Crear usuario
            usuario = Usuario.objects.create(
                username=username,
                email=email,
                password=make_password(contraseña_temporal),
                nombre=nombre,
                rol=rol
            )
            
            # Enviar correo con credenciales
            correo_enviado = AdministratorService.enviar_correo_credenciales(
                email, nombre, username, contraseña_temporal, rol
            )
            
            # Agregar información del estado del correo al usuario
            usuario.correo_enviado = correo_enviado
            usuario.contraseña_temporal = contraseña_temporal
            
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