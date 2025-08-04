from django import forms
from .models import Incidente
from accounts.models import Usuario

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


class AsignarIncidenteForm(forms.Form):
    """Formulario para que los jefes asignen incidentes a analistas"""
    
    analista = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol='analista').order_by('nombre', 'username'),
        empty_label="Seleccione un analista",
        widget=forms.Select(attrs={
            'class': 'form-input',
            'required': True
        }),
        label='Asignar a Analista'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Actualizar queryset para asegurar que solo muestre analistas activos
        self.fields['analista'].queryset = Usuario.objects.filter(
            rol='analista',
            is_active=True
        ).order_by('nombre', 'username')
        
    def clean_analista(self):
        """Validar que el usuario seleccionado sea realmente un analista"""
        analista = self.cleaned_data.get('analista')
        if analista and analista.rol != 'analista':
            raise forms.ValidationError("Solo se pueden asignar incidentes a analistas de seguridad")
        return analista


class ActualizarIncidenteForm(forms.ModelForm):
    """Formulario para que los analistas actualicen incidentes - HU09"""
    
    class Meta:
        model = Incidente
        fields = ['gravedad', 'estado', 'notas_internas']
        widgets = {
            'gravedad': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-input',
                'required': True
            }),
            'notas_internas': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Notas internas para el equipo de seguridad...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar labels personalizados
        self.fields['gravedad'].label = 'Gravedad del Incidente'
        self.fields['estado'].label = 'Estado del Incidente'
        self.fields['notas_internas'].label = 'Notas Internas'
        
        # Solo gravedad y estado son obligatorios
        self.fields['gravedad'].required = True
        self.fields['estado'].required = True
        self.fields['notas_internas'].required = False
        
        # Limitar opciones de estado según criterios de aceptación HU09
        self.fields['estado'].choices = [
            ('pendiente', 'Pendiente'),
            ('en_proceso', 'En Proceso'),
            ('cerrado', 'Cerrado'),
        ]
        
        # Limitar opciones de gravedad según criterios HU09
        self.fields['gravedad'].choices = [
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
        ]
