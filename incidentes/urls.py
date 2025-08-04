from django.urls import path
from . import views

app_name = 'incidentes'

urlpatterns = [
    # URLs para reportantes
    path('reportar/', views.reportar_incidente, name='reportar_incidente'),
    path('mis-incidentes/', views.mis_incidentes, name='mis_incidentes'),
    path('dashboard/', views.dashboard_reportante_incidentes, name='dashboard_reportante_incidentes'),
    
    # URLs para jefes
    path('todos/', views.ver_todos_incidentes, name='ver_todos_incidentes'),
    path('asignar/<int:incidente_id>/', views.asignar_incidente, name='asignar_incidente'),
    
    # URLs para analistas - HU08, HU09, HU10
    path('analista/dashboard/', views.dashboard_analista_incidentes, name='dashboard_analista_incidentes'),
    path('analista/todos/', views.ver_incidentes_analista, name='ver_incidentes_analista'),
    path('analista/actualizar/<int:incidente_id>/', views.actualizar_incidente, name='actualizar_incidente'),
    path('analista/historial/<int:incidente_id>/', views.historial_incidente, name='historial_incidente'),
]
