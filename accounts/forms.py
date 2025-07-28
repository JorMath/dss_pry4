# accounts/forms.py
from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ingrese su correo electrónico'
        })
    )
