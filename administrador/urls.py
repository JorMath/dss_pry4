from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('crear-usuario/', views.crear_usuario_view, name='crear_usuario'),
    path('listar-usuarios/', views.listar_usuarios_view, name='listar_usuarios'),
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
]
