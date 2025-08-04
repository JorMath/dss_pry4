from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from accounts.decorators import rol_required
from .models import Incidente, HistorialCambioIncidente
from .forms import ReportarIncidenteForm, AsignarIncidenteForm, ActualizarIncidenteForm

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
    anio_filtro = request.GET.get('año')
    estado_filtro = request.GET.get('estado')
    gravedad_filtro = request.GET.get('gravedad')
    
    # Empezar con todos los incidentes
    incidentes_query = Incidente.objects.all()
    
    # Aplicar filtros
    if mes_filtro and anio_filtro:
        try:
            mes = int(mes_filtro)
            anio = int(anio_filtro)
            incidentes_query = incidentes_query.filter(
                fecha_reporte__month=mes,
                fecha_reporte__year=anio
            )
        except (ValueError, TypeError):
            pass
    elif anio_filtro:
        try:
            anio = int(anio_filtro)
            incidentes_query = incidentes_query.filter(fecha_reporte__year=anio)
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
    
    # Ordenar por fecha más reciente
    incidentes_query = incidentes_query.order_by('-fecha_reporte')
    
    # Para campos encriptados como gravedad, tenemos que filtrar después de obtener los datos
    if gravedad_filtro:
        # Obtener todos los incidentes que cumplan los otros filtros
        todos_incidentes = list(incidentes_query)
        # Filtrar por gravedad en Python
        incidentes_filtrados = [inc for inc in todos_incidentes if inc.gravedad == gravedad_filtro]
        # Convertir de vuelta a una lista para la paginación
        incidentes_query = incidentes_filtrados
    else:
        # Convertir a lista solo si no hay filtro de gravedad
        pass
    
    # Paginación
    if gravedad_filtro:
        # Para listas filtradas manualmente, usamos una paginación diferente
        paginator = Paginator(incidentes_query, 15)  # incidentes_query es una lista
        page_number = request.GET.get('page')
        incidentes = paginator.get_page(page_number)
        
        # Estadísticas para datos filtrados manualmente
        total_filtrados = len(incidentes_query)
        stats = {
            'total': total_filtrados,
            'pendientes': len([i for i in incidentes_query if i.estado == 'pendiente']),
            'en_proceso': len([i for i in incidentes_query if i.estado in ['en_revision', 'en_proceso']]),
            'resueltos': len([i for i in incidentes_query if i.estado == 'resuelto']),
            'criticos': len([i for i in incidentes_query if i.gravedad == 'critica']),
        }
    else:
        # Paginación normal para QuerySets
        paginator = Paginator(incidentes_query, 15)  # 15 incidentes por página
        page_number = request.GET.get('page')
        incidentes = paginator.get_page(page_number)
        
        # Estadísticas normales
        stats = {
            'total': incidentes_query.count(),
            'pendientes': incidentes_query.filter(estado='pendiente').count(),
            'en_proceso': incidentes_query.filter(estado__in=['en_revision', 'en_proceso']).count(),
            'resueltos': incidentes_query.filter(estado='resuelto').count(),
            'criticos': incidentes_query.filter(gravedad='critica').count(),
        }
    
    # Generar opciones para el filtro de meses y años
    anio_actual = timezone.now().year
    
    # Obtener años de incidentes existentes
    anios_con_incidentes = Incidente.objects.dates('fecha_reporte', 'year').values_list('fecha_reporte__year', flat=True)
    if anios_con_incidentes:
        anio_min = min(anios_con_incidentes)
        anio_max = max(max(anios_con_incidentes), anio_actual)
        anios_disponibles = list(range(anio_min, anio_max + 1))
    else:
        # Si no hay incidentes, mostrar los últimos 3 años y el actual
        anios_disponibles = list(range(anio_actual - 2, anio_actual + 1))
    
    anios_disponibles.sort(reverse=True)  # Mostrar años más recientes primero
    
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
    
    # Usar las opciones definidas en el modelo
    gravedad_choices = Incidente.OPCIONES_GRAVEDAD
    
    context = {
        'incidentes': incidentes,
        'stats': stats,
        'total_incidentes': stats['total'] if gravedad_filtro else incidentes_query.count(),
        'filtros': {
            'mes': mes_filtro,
            'año': anio_filtro,
            'estado': estado_filtro,
            'gravedad': gravedad_filtro,
        },
        'meses': meses,
        'años_disponibles': anios_disponibles,
        'estados_choices': estados_choices,
        'gravedad_choices': gravedad_choices,
        'page_title': 'Todos los Incidentes',
        'page_subtitle': 'Gestión completa de incidentes del sistema'
    }
    return render(request, 'incidentes/todos_incidentes.html', context)


@login_required
@rol_required('jefe')
def asignar_incidente(request, incidente_id):
    """Vista para asignar un incidente a un analista - HU10"""
    incidente = get_object_or_404(Incidente, id=incidente_id)
    
    if request.method == 'POST':
        form = AsignarIncidenteForm(request.POST)
        if form.is_valid():
            analista_anterior = incidente.asignado_a
            nuevo_analista = form.cleaned_data['analista']
            
            # Actualizar la asignación
            incidente.asignado_a = nuevo_analista
            incidente.save()
            
            # Mensaje personalizado según si es asignación o reasignación
            if analista_anterior:
                messages.success(
                    request, 
                    f'Incidente #{incidente.id} reasignado de {analista_anterior.nombre or analista_anterior.username} '
                    f'a {nuevo_analista.nombre or nuevo_analista.username}'
                )
            else:
                messages.success(
                    request, 
                    f'Incidente #{incidente.id} asignado exitosamente a {nuevo_analista.nombre or nuevo_analista.username}'
                )
            
            return redirect('incidentes:ver_todos_incidentes')
    else:
        form = AsignarIncidenteForm()
    
    context = {
        'form': form,
        'incidente': incidente,
        'page_title': 'Asignar Incidente',
        'page_subtitle': f'Asignar incidente #{incidente.id} a un analista'
    }
    return render(request, 'incidentes/asignar_incidente.html', context)


# ====== VISTAS PARA ANALISTAS DE SEGURIDAD ======

@login_required
@rol_required('analista')
def dashboard_analista_incidentes(request):
    """Dashboard específico para analistas con estadísticas de incidentes"""
    # Estadísticas de incidentes asignados al analista
    mis_asignados = Incidente.objects.filter(asignado_a=request.user)
    
    stats = {
        'total': mis_asignados.count(),
        'pendientes': mis_asignados.filter(estado='pendiente').count(),
        'en_proceso': mis_asignados.filter(estado='en_proceso').count(),
        'cerrados': mis_asignados.filter(estado='cerrado').count(),
        'criticos': mis_asignados.filter(gravedad='alta').count(),  # HU09 solo permite baja, media, alta
    }
    
    # Últimos 5 incidentes asignados
    incidentes_recientes = mis_asignados.order_by('-fecha_actualizacion')[:5]
    
    context = {
        'stats': stats,
        'incidentes_recientes': incidentes_recientes,
        'page_title': 'Dashboard Analista',
        'page_subtitle': 'Gestión de incidentes asignados'
    }
    return render(request, 'incidentes/dashboard_analista_incidentes.html', context)


@login_required
@rol_required('analista')
def ver_incidentes_analista(request):
    """Vista para que el analista vea todos los incidentes registrados - HU08"""
    from django.utils import timezone
    
    # Obtener parámetros de filtro
    tipo_filtro = request.GET.get('tipo')
    estado_filtro = request.GET.get('estado')
    gravedad_filtro = request.GET.get('gravedad')
    asignado_filtro = request.GET.get('asignado_a')
    
    # Empezar con todos los incidentes
    incidentes_query = Incidente.objects.all()
    
    # Aplicar filtro de estado
    if estado_filtro and estado_filtro != '':
        incidentes_query = incidentes_query.filter(estado=estado_filtro)
    
    # Aplicar filtro de asignado
    if asignado_filtro and asignado_filtro != '':
        if asignado_filtro == 'sin_asignar':
            incidentes_query = incidentes_query.filter(asignado_a__isnull=True)
        else:
            try:
                asignado_id = int(asignado_filtro)
                incidentes_query = incidentes_query.filter(asignado_a_id=asignado_id)
            except (ValueError, TypeError):
                pass
    
    # Ordenar por fecha más reciente
    incidentes_query = incidentes_query.order_by('-fecha_reporte')
    
    # Convertir a lista para manejar campos encriptados
    todos_incidentes = list(incidentes_query)
    
    # Aplicar filtros de campos encriptados manualmente
    if tipo_filtro and tipo_filtro != '':
        todos_incidentes = [inc for inc in todos_incidentes if inc.tipo == tipo_filtro]
    
    if gravedad_filtro and gravedad_filtro != '':
        todos_incidentes = [inc for inc in todos_incidentes if inc.gravedad == gravedad_filtro]
    
    # Paginación
    paginator = Paginator(todos_incidentes, 15)
    page_number = request.GET.get('page')
    incidentes = paginator.get_page(page_number)
    
    # Estadísticas para todos los incidentes filtrados
    stats = {
        'total': len(todos_incidentes),
        'pendientes': len([i for i in todos_incidentes if i.estado == 'pendiente']),
        'en_proceso': len([i for i in todos_incidentes if i.estado == 'en_proceso']),
        'cerrados': len([i for i in todos_incidentes if i.estado == 'cerrado']),
        'criticos': len([i for i in todos_incidentes if i.gravedad == 'critica']),
    }
    
    # Opciones para filtros
    from accounts.models import Usuario
    analistas = Usuario.objects.filter(rol='analista')
    
    tipos_choices = [
        ('bug_seguridad', 'Bug de Seguridad'),
        ('acceso_no_autorizado', 'Acceso No Autorizado'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('ddos', 'DDoS'),
        ('fuga_datos', 'Fuga de Datos'),
        ('vulnerabilidad_sistema', 'Vulnerabilidad del Sistema'),
        ('otro', 'Otro'),
    ]
    
    estados_choices = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('cerrado', 'Cerrado'),
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
        'filtros': {
            'tipo': tipo_filtro,
            'estado': estado_filtro,
            'gravedad': gravedad_filtro,
            'asignado_a': asignado_filtro,
        },
        'tipos_choices': tipos_choices,
        'estados_choices': estados_choices,
        'gravedad_choices': gravedad_choices,
        'analistas': analistas,
        'page_title': 'Todos los Incidentes',
        'page_subtitle': 'Vista completa de incidentes para análisis'
    }
    
    return render(request, 'incidentes/ver_incidentes_analista.html', context)


@login_required
@rol_required('analista')
def actualizar_incidente(request, incidente_id):
    """Vista para que los analistas actualicen incidentes - HU09"""
    incidente = get_object_or_404(Incidente, id=incidente_id)
    
    if request.method == 'POST':
        # Guardar valores anteriores ANTES de crear el formulario
        valores_anteriores = {
            'gravedad': incidente.gravedad,
            'estado': incidente.estado,
            'notas_internas': incidente.notas_internas or ''
        }
        
        form = ActualizarIncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            # Actualizar el incidente
            incidente_actualizado = form.save()
            
            # Debug: imprimir los valores para verificar
            print(f"Valores anteriores: {valores_anteriores}")
            print(f"Valores nuevos: gravedad={incidente_actualizado.gravedad}, estado={incidente_actualizado.estado}, notas={incidente_actualizado.notas_internas}")
            
            # Registrar cambios en el historial - HU10
            cambios_registrados = 0
            for campo in ['gravedad', 'estado', 'notas_internas']:
                valor_anterior = str(valores_anteriores[campo]) if valores_anteriores[campo] else ''
                valor_nuevo = str(getattr(incidente_actualizado, campo)) if getattr(incidente_actualizado, campo) else ''
                
                print(f"Comparando {campo}: '{valor_anterior}' vs '{valor_nuevo}'")
                
                if valor_anterior != valor_nuevo:
                    historial_creado = HistorialCambioIncidente.objects.create(
                        incidente=incidente_actualizado,
                        usuario_modificacion=request.user,
                        campo_modificado=campo,
                        valor_anterior=valor_anterior,
                        valor_nuevo=valor_nuevo,
                        descripcion=f"Cambió {campo} de '{valor_anterior}' a '{valor_nuevo}'"
                    )
                    cambios_registrados += 1
                    print(f"Creado historial #{historial_creado.id} para campo {campo}")
            
            print(f"Total cambios registrados en historial: {cambios_registrados}")
            
            # Verificar que se creó el historial
            total_historial = HistorialCambioIncidente.objects.filter(incidente=incidente_actualizado).count()
            print(f"Total registros en historial para este incidente: {total_historial}")
            
            messages.success(
                request,
                f'Incidente #{incidente.id} actualizado exitosamente. '
                f'Gravedad: {incidente_actualizado.get_gravedad_display()}, '
                f'Estado: {incidente_actualizado.get_estado_display()}. '
                f'Se registraron {cambios_registrados} cambios en el historial.'
            )
            
            return redirect('incidentes:ver_incidentes_analista')
    else:
        form = ActualizarIncidenteForm(instance=incidente)
    
    context = {
        'form': form,
        'incidente': incidente,
        'page_title': 'Actualizar Incidente',
        'page_subtitle': f'Clasificar y actualizar incidente #{incidente.id}'
    }
    return render(request, 'incidentes/actualizar_incidente.html', context)


@login_required
@rol_required('analista')
def historial_incidente(request, incidente_id):
    """Vista para ver el historial de cambios de un incidente - HU10"""
    incidente = get_object_or_404(Incidente, id=incidente_id)
    
    # Obtener historial de cambios ordenado por fecha más reciente
    historial = HistorialCambioIncidente.objects.filter(incidente=incidente).order_by('-fecha_cambio')
    
    # Debug: verificar que se obtienen registros
    total_registros = historial.count()
    print(f"Historial para incidente #{incidente_id}: {total_registros} registros encontrados")
    
    if total_registros > 0:
        print("Primeros 3 registros:")
        for i, cambio in enumerate(historial[:3]):
            print(f"  {i+1}. Campo: {cambio.campo_modificado}, Usuario: {cambio.usuario_modificacion.username}, Fecha: {cambio.fecha_cambio}")
    
    # Paginación del historial
    paginator = Paginator(historial, 10)  # 10 cambios por página
    page_number = request.GET.get('page')
    historial_paginado = paginator.get_page(page_number)
    
    print(f"Página actual: {historial_paginado.number}, Total páginas: {paginator.num_pages}")
    print(f"Registros en página actual: {len(historial_paginado.object_list)}")
    
    context = {
        'incidente': incidente,
        'historial': historial_paginado,
        'total_cambios': historial.count(),
        'page_title': 'Historial de Incidente',
        'page_subtitle': f'Historial de cambios del incidente #{incidente.id}'
    }
    return render(request, 'incidentes/historial_incidente.html', context)
