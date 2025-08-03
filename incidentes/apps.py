from django.apps import AppConfig

class IncidentesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incidentes'

    def ready(self):
        # Registro de auditoría para el modelo Incidente
        from auditlog.registry import auditlog
        from .models import Incidente
        auditlog.register(Incidente)
