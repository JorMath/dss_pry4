from django import forms
from accounts.models import Usuario

class CrearUsuarioForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre de usuario'})
    )
    
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'usuario@empresa.com'})
    )
    
    nombre = forms.CharField(
        max_length=100,
        label='Nombre completo',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre completo'})
    )
    
    rol = forms.ChoiceField(
        choices=Usuario.ROL_CHOICES,
        label='Rol del usuario',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya existe")
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado")
        return email
