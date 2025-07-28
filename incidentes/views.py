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
