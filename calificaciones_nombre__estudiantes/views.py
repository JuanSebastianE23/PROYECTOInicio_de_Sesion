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
