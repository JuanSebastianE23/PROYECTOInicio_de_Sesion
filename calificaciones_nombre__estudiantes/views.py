from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg
from .models import Calificacion
from .forms import CalificacionForm

# Vista de inicio de sesión
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {username}!')
            return redirect('listar_calificaciones')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    return render(request, 'calificaciones/login.html')

# Vista de cierre de sesión
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

# Vista para crear una nueva calificación
@login_required
def crear_calificacion(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación registrada exitosamente')
            return redirect('listar_calificaciones')
    else:
        form = CalificacionForm()
    return render(request, 'calificaciones/crear.html', {'form': form})

# Vista para listar todas las calificaciones
@login_required
def listar_calificaciones(request):
    """Lista calificaciones con búsqueda, filtros y paginación"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Obtener todas las calificaciones
    calificaciones = Calificacion.objects.all()
    
    # Búsqueda por nombre o identificación
    buscar = request.GET.get('buscar', '')
    if buscar:
        calificaciones = calificaciones.filter(
            Q(nombre_estudiante__icontains=buscar) |
            Q(identificacion__icontains=buscar)
        )
    
    # Filtro por asignatura
    asignatura_filtro = request.GET.get('asignatura', '')
    if asignatura_filtro:
        calificaciones = calificaciones.filter(asignatura__icontains=asignatura_filtro)
    
    # Ordenamiento
    orden = request.GET.get('orden', '-promedio')
    calificaciones = calificaciones.order_by(orden)
    
    # Paginación (10 por página)
    paginator = Paginator(calificaciones, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Promedio general (de todos, no solo de la página)
    promedio_general = Calificacion.objects.all().aggregate(Avg('promedio'))['promedio__avg']
    if promedio_general is not None:
        promedio_general = round(promedio_general, 2)
    
    # Obtener lista de asignaturas únicas para el filtro
    asignaturas = Calificacion.objects.values_list('asignatura', flat=True).distinct().order_by('asignatura')
    
    context = {
        'page_obj': page_obj,
        'calificaciones': page_obj,  # Para compatibilidad con template
        'promedio_general': promedio_general,
        'buscar': buscar,
        'asignatura_filtro': asignatura_filtro,
        'orden': orden,
        'asignaturas': asignaturas,
    }
    return render(request, 'calificaciones/listar.html', context)

# Vista para editar una calificación existente
@login_required
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada exitosamente')
            return redirect('listar_calificaciones')
    else:
        form = CalificacionForm(instance=calificacion)
    return render(request, 'calificaciones/editar.html', {'form': form, 'calificacion': calificacion})

# Vista para eliminar una calificación
@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    if request.method == 'POST':
        calificacion.delete()
        messages.success(request, 'Calificación eliminada exitosamente')
        return redirect('listar_calificaciones')
    return render(request, 'calificaciones/eliminar.html', {'calificacion': calificacion})

# Vista para mostrar el promedio general
@login_required
def promedio_general(request):
    promedio = Calificacion.objects.all().aggregate(Avg('promedio'))['promedio__avg']
    if promedio is not None:
        promedio = round(promedio, 2)
    calificaciones = Calificacion.objects.all()
    context = {
        'promedio_general': promedio,
        'total_estudiantes': calificaciones.count()
    }
    return render(request, 'calificaciones/promedio_general.html', context)


# Vista de estadísticas avanzadas
@login_required
def estadisticas(request):
    """Muestra estadísticas detalladas del sistema"""
    from django.db.models import Avg, Max, Min, Count
    
    # Estadísticas generales
    total_calificaciones = Calificacion.objects.count()
    promedio_general = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']
    promedio_mas_alto = Calificacion.objects.aggregate(Max('promedio'))['promedio__max']
    promedio_mas_bajo = Calificacion.objects.aggregate(Min('promedio'))['promedio__min']
    
    # Mejor y peor estudiante
    mejor_estudiante = Calificacion.objects.order_by('-promedio').first()
    peor_estudiante = Calificacion.objects.order_by('promedio').first()
    
    # Promedio por asignatura
    promedios_por_asignatura = Calificacion.objects.values('asignatura').annotate(
        promedio=Avg('promedio'),
        total=Count('id')
    ).order_by('-promedio')
    
    # Estudiantes aprobados vs reprobados
    aprobados = Calificacion.objects.filter(promedio__gte=60).count()
    reprobados = Calificacion.objects.filter(promedio__lt=60).count()
    
    # Redondear valores
    if promedio_general:
        promedio_general = round(promedio_general, 2)
    if promedio_mas_alto:
        promedio_mas_alto = round(promedio_mas_alto, 2)
    if promedio_mas_bajo:
        promedio_mas_bajo = round(promedio_mas_bajo, 2)
    
    for item in promedios_por_asignatura:
        item['promedio'] = round(item['promedio'], 2)
    
    context = {
        'total_calificaciones': total_calificaciones,
        'promedio_general': promedio_general,
        'promedio_mas_alto': promedio_mas_alto,
        'promedio_mas_bajo': promedio_mas_bajo,
        'mejor_estudiante': mejor_estudiante,
        'peor_estudiante': peor_estudiante,
        'promedios_por_asignatura': promedios_por_asignatura,
        'aprobados': aprobados,
        'reprobados': reprobados,
    }
    return render(request, 'calificaciones/estadisticas.html', context)


# Vista para exportar calificaciones a CSV
@login_required
def exportar_csv(request):
    """Exporta todas las calificaciones a un archivo CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="calificaciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff')  # BOM para Excel
    
    writer = csv.writer(response)
    writer.writerow(['Nombre Estudiante', 'Identificación', 'Asignatura', 'Nota 1', 'Nota 2', 'Nota 3', 'Promedio'])
    
    calificaciones = Calificacion.objects.all().order_by('-promedio')
    for cal in calificaciones:
        writer.writerow([
            cal.nombre_estudiante,
            cal.identificacion,
            cal.asignatura,
            cal.nota1,
            cal.nota2,
            cal.nota3,
            cal.promedio
        ])
    
    return response


# Vista para importar calificaciones desde CSV
@login_required
def importar_csv(request):
    """Importa calificaciones desde un archivo CSV"""
    if request.method == 'POST' and request.FILES.get('archivo_csv'):
        import csv
        import io
        
        archivo = request.FILES['archivo_csv']
        
        # Validar extensión
        if not archivo.name.endswith('.csv'):
            messages.error(request, 'El archivo debe ser CSV')
            return redirect('listar_calificaciones')
        
        try:
            # Leer archivo
            decoded_file = archivo.read().decode('utf-8-sig')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            importados = 0
            errores = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validar que existan las columnas necesarias
                    nombre = row.get('Nombre Estudiante', '').strip()
                    identificacion = row.get('Identificación', '').strip()
                    asignatura = row.get('Asignatura', '').strip()
                    nota1 = row.get('Nota 1', '').strip()
                    nota2 = row.get('Nota 2', '').strip()
                    nota3 = row.get('Nota 3', '').strip()
                    
                    if not all([nombre, identificacion, asignatura, nota1, nota2, nota3]):
                        errores.append(f'Fila {row_num}: Datos incompletos')
                        continue
                    
                    # Verificar duplicados
                    if Calificacion.objects.filter(identificacion=identificacion, asignatura=asignatura).exists():
                        errores.append(f'Fila {row_num}: Ya existe {identificacion} en {asignatura}')
                        continue
                    
                    # Crear calificación
                    Calificacion.objects.create(
                        nombre_estudiante=nombre,
                        identificacion=identificacion,
                        asignatura=asignatura,
                        nota1=Decimal(nota1),
                        nota2=Decimal(nota2),
                        nota3=Decimal(nota3)
                    )
                    importados += 1
                    
                except Exception as e:
                    errores.append(f'Fila {row_num}: {str(e)}')
            
            # Mensajes de resultado
            if importados > 0:
                messages.success(request, f'Se importaron {importados} calificaciones exitosamente')
            if errores:
                messages.warning(request, f'Errores encontrados: {len(errores)}. ' + '; '.join(errores[:5]))
            
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')
        
        return redirect('listar_calificaciones')
    
    return render(request, 'calificaciones/importar_csv.html')
