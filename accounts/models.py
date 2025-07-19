from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('reportante', 'Usuario Reportante'),
        ('analista', 'Analista de Seguridad'),
        ('jefe', 'Jefe de Seguridad'),
    ]
    nombre = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(unique=True, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
