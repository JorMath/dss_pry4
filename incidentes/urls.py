from django.urls import path
from . import views

app_name = 'incidentes'

urlpatterns = [
    path('reportar/', views.reportar_incidente, name='reportar_incidente'),
    path('mis-incidentes/', views.mis_incidentes, name='mis_incidentes'),
    path('dashboard/', views.dashboard_reportante_incidentes, name='dashboard_reportante_incidentes'),
    path('todos/', views.ver_todos_incidentes, name='ver_todos_incidentes'),
]
