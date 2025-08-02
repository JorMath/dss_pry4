"""
Campos de modelo personalizados para cifrado automático de datos.
"""

from django.db import models
from django.core.exceptions import ValidationError
from .encryption import FieldEncryption


class EncryptedCharField(models.CharField):
    """
    Campo CharField que cifra automáticamente los datos al guardar
    y los descifra al recuperar de la base de datos.
    """
    
    description = "Campo de texto cifrado automáticamente"
    
    def __init__(self, *args, **kwargs):
        # Aumentar max_length por defecto para acomodar el texto cifrado
        if 'max_length' in kwargs:
            # El texto cifrado puede ser significativamente más largo
            # Aumentamos el tamaño para acomodar el cifrado
            kwargs['max_length'] = kwargs['max_length'] * 4
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """
        Convierte el valor de la base de datos al valor Python.
        Descifra automáticamente el valor.
        """
        if value is None:
            return value
        
        try:
            return FieldEncryption.decrypt(value)
        except Exception:
            # Si hay error al descifrar, devolver el valor original
            # Esto permite migración gradual de datos existentes
            return value
    
    def to_python(self, value):
        """
        Convierte el valor a tipo Python.
        """
        if value is None:
            return value
        
        # Si ya es una cadena, verificar si está cifrada
        if isinstance(value, str):
            try:
                # Intentar descifrar para verificar si ya está cifrado
                decrypted = FieldEncryption.decrypt(value)
                return decrypted
            except Exception:
                # Si no se puede descifrar, asumir que es texto plano
                return value
        
        return str(value)
    
    def get_prep_value(self, value):
        """
        Prepara el valor para guardar en la base de datos.
        Cifra automáticamente el valor.
        """
        if value is None or value == '':
            return value
        
        # Convertir a string si no lo es
        if not isinstance(value, str):
            value = str(value)
        
        # Cifrar el valor antes de guardarlo
        try:
            return FieldEncryption.encrypt(value)
        except Exception as e:
            raise ValidationError(f"Error al cifrar el valor: {e}")
    
    def value_to_string(self, obj):
        """
        Convierte el valor del objeto a string para serialización.
        Devuelve el valor descifrado.
        """
        value = self.value_from_object(obj)
        return self.to_python(value) if value is not None else ''


class EncryptedEmailField(models.EmailField):
    """
    Campo EmailField que cifra automáticamente los emails al guardar
    y los descifra al recuperar de la base de datos.
    """
    
    description = "Campo de email cifrado automáticamente"
    
    def __init__(self, *args, **kwargs):
        # Aumentar max_length por defecto para acomodar el email cifrado
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 1000  # Espacio suficiente para emails cifrados
        else:
            kwargs['max_length'] = kwargs['max_length'] * 4
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        """
        Convierte el valor de la base de datos al valor Python.
        Descifra automáticamente el valor.
        """
        if value is None:
            return value
        
        try:
            return FieldEncryption.decrypt(value)
        except Exception:
            # Si hay error al descifrar, devolver el valor original
            return value
    
    def to_python(self, value):
        """
        Convierte el valor a tipo Python y valida el formato de email.
        """
        if value is None:
            return value
        
        # Si ya es una cadena, verificar si está cifrada
        if isinstance(value, str):
            try:
                # Intentar descifrar para verificar si ya está cifrado
                decrypted = FieldEncryption.decrypt(value)
                # Validar que el email descifrado tenga formato válido
                return super().to_python(decrypted)
            except Exception:
                # Si no se puede descifrar, asumir que es texto plano
                return super().to_python(value)
        
        return super().to_python(value)
    
    def get_prep_value(self, value):
        """
        Prepara el valor para guardar en la base de datos.
        Valida el email y luego lo cifra.
        """
        if value is None or value == '':
            return value
        
        # Validar formato de email primero
        validated_value = super().to_python(value)
        
        # Cifrar el email validado
        try:
            return FieldEncryption.encrypt(validated_value)
        except Exception as e:
            raise ValidationError(f"Error al cifrar el email: {e}")
    
    def value_to_string(self, obj):
        """
        Convierte el valor del objeto a string para serialización.
        Devuelve el email descifrado.
        """
        value = self.value_from_object(obj)
        return self.to_python(value) if value is not None else ''
