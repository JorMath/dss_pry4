"""
Módulo para manejo de cifrado de campos en la base de datos.
Utiliza cifrado simétrico AES para proteger datos sensibles.
"""

import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class FieldEncryption:
    """Maneja el cifrado y descifrado de campos usando Fernet."""
    
    _fernet = None
    
    @classmethod
    def get_fernet(cls):
        """Obtiene la instancia de Fernet para cifrado/descifrado."""
        if cls._fernet is None:
            cls._fernet = cls._create_fernet()
        return cls._fernet
    
    @classmethod
    def _create_fernet(cls):
        """Crea una instancia de Fernet usando la clave secreta de Django."""
        # Usar la SECRET_KEY de Django como base para generar la clave de cifrado
        secret_key = getattr(settings, 'SECRET_KEY', None)
        if not secret_key:
            raise ImproperlyConfigured("SECRET_KEY no está configurado en settings")
        
        # Generar una clave derivada de la SECRET_KEY
        password = secret_key.encode('utf-8')
        salt_value = getattr(settings, 'ENCRYPTION_SALT', 'django_field_encryption_salt')
        salt = salt_value.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    @classmethod
    def encrypt(cls, value):
        """
        Cifra un valor de texto.
        
        Args:
            value (str): El texto a cifrar
            
        Returns:
            str: El texto cifrado en base64
        """
        if value is None or value == '':
            return value
        
        fernet = cls.get_fernet()
        encrypted_bytes = fernet.encrypt(value.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
    
    @classmethod
    def decrypt(cls, encrypted_value):
        """
        Descifra un valor cifrado.
        
        Args:
            encrypted_value (str): El texto cifrado en base64
            
        Returns:
            str: El texto original descifrado
        """
        if encrypted_value is None or encrypted_value == '':
            return encrypted_value
        
        try:
            fernet = cls.get_fernet()
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode('utf-8'))
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception:
            # Si no se puede descifrar, asumir que es texto plano (para migración)
            return encrypted_value
