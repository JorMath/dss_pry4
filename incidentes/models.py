from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Incidente(models.Model):
    TIPOS_INCIDENTE = [
        ('bug', 'Bug de Seguridad'),
        ('acceso_no_autorizado', 'Acceso No Autorizado'),
        ('phishing', 'Intento de Phishing'),
        ('malware', 'Detección de Malware'),
        ('fuga_datos', 'Fuga de Datos'),
        ('vulnerabilidad', 'Vulnerabilidad del Sistema'),
        ('otro', 'Otro'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    ]
    
    OPCIONES_GRAVEDAD = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    tipo = models.CharField(
        max_length=50,
        choices=TIPOS_INCIDENTE,
        verbose_name='Tipo de Incidente'
    )
    descripcion = models.TextField(
        verbose_name='Descripción del Incidente',
        help_text='Describa detalladamente el incidente de seguridad'
    )
    fecha_reporte = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Reporte'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente',
        verbose_name='Estado'
    )
    gravedad = models.CharField(
        max_length=20,
        choices=OPCIONES_GRAVEDAD,
        default='media',
        verbose_name='Gravedad'
    )
    reportado_por = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incidentes_reportados',
        verbose_name='Reportado por'
    )
    asignado_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidentes_asignados',
        verbose_name='Asignado a'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    notas_internas = models.TextField(
        blank=True,
        verbose_name='Notas Internas',
        help_text='Notas para uso interno del equipo de seguridad'
    )
    
    class Meta:
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
        ordering = ['-fecha_reporte']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.reportado_por.username} - {self.fecha_reporte.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para asignar gravedad automáticamente según el tipo"""
        if not self.pk:  # Solo en la creación inicial
            # Mapeo de tipos de incidente a gravedad
            gravedad_por_tipo = {
                'bug_seguridad': 'alta',
                'acceso_no_autorizado': 'critica',
                'malware': 'media',
                'phishing': 'alta',
                'ddos': 'critica',
                'fuga_datos': 'critica',
                'otro': 'baja'
            }
            # Asignar gravedad basada en el tipo
            self.gravedad = gravedad_por_tipo.get(self.tipo, 'media')
        
        super().save(*args, **kwargs)
    
    def get_gravedad_color(self):
        """Retorna el color CSS basado en la gravedad"""
        colors = {
            'baja': '#28a745',
            'media': '#ffc107',
            'alta': '#fd7e14',
            'critica': '#dc3545'
        }
        return colors.get(self.gravedad, '#6c757d')
    
    def get_estado_color(self):
        """Retorna el color CSS basado en el estado"""
        colors = {
            'pendiente': '#dc3545',
            'en_revision': '#ffc107',
            'en_proceso': '#fd7e14',
            'resuelto': '#28a745',
            'cerrado': '#6c757d'
        }
        return colors.get(self.estado, '#6c757d')
