from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from accounts.decorators import rol_required
from .models import Incidente
from .forms import ReportarIncidenteForm

@login_required
@rol_required('reportante')
def reportar_incidente(request):
    """Vista para reportar un nuevo incidente - HU01"""
    if request.method == 'POST':
        form = ReportarIncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(user=request.user)
            messages.success(
                request, 
                f'¡Incidente reportado correctamente! '
                f'Se ha registrado con estado "Pendiente" y gravedad "{incidente.get_gravedad_display()}". '
                f'ID del incidente: #{incidente.id}'
            )
            return redirect('incidentes:mis_incidentes')
    else:
        form = ReportarIncidenteForm()
    
    context = {
        'form': form,
        'page_title': 'Reportar Incidente',
        'page_subtitle': 'Registre un nuevo incidente de seguridad'
    }
    return render(request, 'incidentes/reportar_incidente.html', context)

@login_required
@rol_required('reportante')
def mis_incidentes(request):
    """Vista para ver incidentes reportados por el usuario - HU02"""
    incidentes_list = Incidente.objects.filter(reportado_por=request.user)
    
    # Paginación
    paginator = Paginator(incidentes_list, 10)  # 10 incidentes por página
    page_number = request.GET.get('page')
    incidentes = paginator.get_page(page_number)
    
    context = {
        'incidentes': incidentes,
        'total_incidentes': incidentes_list.count(),
        'page_title': 'Mis Incidentes Reportados',
        'page_subtitle': 'Lista de incidentes que ha reportado'
    }
    return render(request, 'incidentes/mis_incidentes.html', context)

@login_required
@rol_required('reportante')
def dashboard_reportante_incidentes(request):
    """Dashboard específico para reportantes con estadísticas de incidentes"""
    # Estadísticas del usuario
    mis_incidentes = Incidente.objects.filter(reportado_por=request.user)
    
    stats = {
        'total': mis_incidentes.count(),
        'pendientes': mis_incidentes.filter(estado='pendiente').count(),
        'en_proceso': mis_incidentes.filter(estado__in=['en_revision', 'en_proceso']).count(),
        'resueltos': mis_incidentes.filter(estado='resuelto').count(),
    }
    
    # Últimos 5 incidentes
    ultimos_incidentes = mis_incidentes[:5]
    
    context = {
        'stats': stats,
        'ultimos_incidentes': ultimos_incidentes,
        'page_title': 'Panel de Incidentes',
        'page_subtitle': 'Gestión de sus incidentes reportados'
    }
    return render(request, 'incidentes/dashboard_reportante.html', context)

@login_required
@rol_required('jefe')
def ver_todos_incidentes(request):
    """Vista para que el jefe vea todos los incidentes con filtros"""
    from django.utils import timezone
    from datetime import datetime
    import calendar
    
    # Obtener parámetros de filtro
    mes_filtro = request.GET.get('mes')
    año_filtro = request.GET.get('año')
    estado_filtro = request.GET.get('estado')
    gravedad_filtro = request.GET.get('gravedad')
    
    # Empezar con todos los incidentes
    incidentes_query = Incidente.objects.all()
    
    # Aplicar filtros
    if mes_filtro and año_filtro:
        try:
            mes = int(mes_filtro)
            año = int(año_filtro)
            incidentes_query = incidentes_query.filter(
                fecha_reporte__month=mes,
                fecha_reporte__year=año
            )
        except (ValueError, TypeError):
            pass
    elif año_filtro:
        try:
            año = int(año_filtro)
            incidentes_query = incidentes_query.filter(fecha_reporte__year=año)
        except (ValueError, TypeError):
            pass
    elif mes_filtro:
        try:
            mes = int(mes_filtro)
            incidentes_query = incidentes_query.filter(fecha_reporte__month=mes)
        except (ValueError, TypeError):
            pass
    
    if estado_filtro:
        incidentes_query = incidentes_query.filter(estado=estado_filtro)
    
    if gravedad_filtro:
        incidentes_query = incidentes_query.filter(gravedad=gravedad_filtro)
    
    # Ordenar por fecha más reciente
    incidentes_query = incidentes_query.order_by('-fecha_reporte')
    
    # Paginación
    paginator = Paginator(incidentes_query, 15)  # 15 incidentes por página
    page_number = request.GET.get('page')
    incidentes = paginator.get_page(page_number)
    
    # Estadísticas generales
    stats = {
        'total': incidentes_query.count(),
        'pendientes': incidentes_query.filter(estado='pendiente').count(),
        'en_proceso': incidentes_query.filter(estado__in=['en_revision', 'en_proceso']).count(),
        'resueltos': incidentes_query.filter(estado='resuelto').count(),
        'criticos': incidentes_query.filter(gravedad='critica').count(),
    }
    
    # Generar opciones para el filtro de meses y años
    año_actual = timezone.now().year
    
    # Obtener años de incidentes existentes
    años_con_incidentes = Incidente.objects.dates('fecha_reporte', 'year').values_list('fecha_reporte__year', flat=True)
    if años_con_incidentes:
        año_min = min(años_con_incidentes)
        año_max = max(max(años_con_incidentes), año_actual)
        años_disponibles = list(range(año_min, año_max + 1))
    else:
        # Si no hay incidentes, mostrar los últimos 3 años y el actual
        años_disponibles = list(range(año_actual - 2, año_actual + 1))
    
    años_disponibles.sort(reverse=True)  # Mostrar años más recientes primero
    
    meses = [
        (1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'),
        (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'),
        (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')
    ]
    
    # Opciones para filtros
    estados_choices = [
        ('pendiente', 'Pendiente'),
        ('en_revision', 'En Revisión'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
        ('rechazado', 'Rechazado'),
    ]
    
    gravedad_choices = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    context = {
        'incidentes': incidentes,
        'stats': stats,
        'total_incidentes': incidentes_query.count(),
        'filtros': {
            'mes': mes_filtro,
            'año': año_filtro,
            'estado': estado_filtro,
            'gravedad': gravedad_filtro,
        },
        'meses': meses,
        'años_disponibles': años_disponibles,
        'estados_choices': estados_choices,
        'gravedad_choices': gravedad_choices,
        'page_title': 'Todos los Incidentes',
        'page_subtitle': 'Gestión completa de incidentes del sistema'
    }
    return render(request, 'incidentes/todos_incidentes.html', context)
