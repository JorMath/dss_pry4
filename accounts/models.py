from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from .fields import EncryptedCharField, EncryptedEmailField
from .encryption import FieldEncryption

class UsuarioManager(UserManager):
    """Manager personalizado para manejar búsquedas con campos cifrados."""
    
    def get_by_email(self, email_plain):
        """Buscar usuario por email en texto plano."""
        # Como el cifrado es no determinista, necesitamos buscar descifrado
        for user in self.all():
            try:
                if user.email_plain == email_plain:
                    return user
            except Exception:
                # Si hay error al descifrar, continuar con el siguiente
                continue
        
        # Si no se encontró, lanzar excepción
        raise self.model.DoesNotExist(f"Usuario con email {email_plain} no encontrado")
    
    def filter_by_email(self, email_plain):
        """Filtrar usuarios por email en texto plano."""
        # Como el cifrado es no determinista, necesitamos filtrar descifrado
        matching_users = []
        for user in self.all():
            try:
                if user.email_plain == email_plain:
                    matching_users.append(user.pk)
            except Exception:
                # Si hay error al descifrar, continuar con el siguiente
                continue
        
        return self.filter(pk__in=matching_users)
    
    def filter_by_email_contains(self, email_substring):
        """Filtrar usuarios por substring en email en texto plano."""
        # Obtener todos los usuarios y filtrar en memoria por el email descifrado
        all_users = self.all()
        matching_users = []
        
        for user in all_users:
            try:
                # Obtener el email en texto plano
                plain_email = user.email_plain
                if plain_email and email_substring in plain_email:
                    matching_users.append(user.pk)
            except Exception:
                # Si hay error al descifrar, ignorar este usuario
                continue
        
        # Retornar un queryset con los usuarios que coinciden
        return self.filter(pk__in=matching_users)
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Crear un usuario normal con campos cifrados.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        # NO cifrar el email aquí, dejarlo como está para que lo maneje save()
        user = self._create_user(username, email, password, **extra_fields)
        
        # Forzar el guardado para activar el cifrado en save()
        if email and user.email:
            user.save()  # Esto debería cifrar el email
        
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Crear un superusuario con campos cifrados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('reportante', 'Usuario Reportante'),
        ('analista', 'Analista de Seguridad'),
        ('jefe', 'Jefe de Seguridad'),
    ]
    nombre = EncryptedCharField(max_length=100, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    
    # Usar el manager personalizado
    objects = UsuarioManager()
    
    def save(self, *args, **kwargs):
        """Cifrar el email antes de guardar usando el campo email existente."""
        if self.email:
            # Verificar si el email ya está cifrado de forma más robusta
            is_encrypted = False
            try:
                # Un email cifrado debería ser mucho más largo y contener caracteres base64
                if len(self.email) > 50 and ('=' in self.email or len(self.email) > 100):
                    # Intentar descifrar para confirmar
                    decrypted = FieldEncryption.decrypt(self.email)
                    # Si el descifrado produce algo diferente al original, está cifrado
                    if decrypted != self.email:
                        is_encrypted = True
                    else:
                        is_encrypted = False
                else:
                    # Email muy corto o sin características de base64, no está cifrado
                    is_encrypted = False
            except Exception:
                # Si hay excepción al descifrar, definitivamente no está cifrado
                is_encrypted = False
            
            # Solo cifrar si no está ya cifrado
            if not is_encrypted:
                self.email = FieldEncryption.encrypt(self.email)
        
        super().save(*args, **kwargs)
    
    @property
    def email_plain(self):
        """Propiedad para obtener el email en texto plano."""
        if self.email:
            try:
                return FieldEncryption.decrypt(self.email)
            except:
                return self.email
        return self.email
    
    @email_plain.setter
    def email_plain(self, value):
        """Setter para establecer el email en texto plano."""
        self.email = value  # Se cifrará automáticamente en save()
    
    def get_email_decrypted(self):
        """Método para obtener el email en texto plano (compatibilidad)."""
        return self.email_plain
    
    def set_email_plain(self, email_plain):
        """Método para establecer el email en texto plano (compatibilidad)."""
        self.email_plain = email_plain
