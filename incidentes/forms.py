from django import forms
from .models import Incidente

class ReportarIncidenteForm(forms.ModelForm):
    """Formulario para que los usuarios reportantes creen incidentes"""
    
    class Meta:
        model = Incidente
        fields = ['tipo', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 5,
                'placeholder': 'Describa detalladamente el incidente de seguridad...',
                'required': True
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar labels personalizados
        self.fields['tipo'].label = 'Tipo de Incidente'
        self.fields['descripcion'].label = 'Descripción del Incidente'
        
        # Hacer todos los campos obligatorios
        for field in self.fields.values():
            field.required = True
            
    def save(self, commit=True, user=None):
        """Sobrescribir save para asignar automáticamente el usuario reportante"""
        incidente = super().save(commit=False)
        if user:
            incidente.reportado_por = user
            
        # Asignar gravedad automáticamente basada en el tipo
        gravedad_por_tipo = {
            'bug': 'alta',
            'acceso_no_autorizado': 'critica',
            'phishing': 'alta',
            'malware': 'critica',
            'fuga_datos': 'critica',
            'vulnerabilidad': 'alta',
            'otro': 'media'
        }
        incidente.gravedad = gravedad_por_tipo.get(incidente.tipo, 'media')
        
        if commit:
            incidente.save()
        return incidente
