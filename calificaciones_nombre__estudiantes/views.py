from django.shortcuts import render, redirect, get_object_or_404 
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Avg
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Calificacion
from .forms import CalificacionForm


def inicio(request):
    if request.user.is_authenticated:
        return redirect('listar_calificaciones')
    return redirect('login')


# LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'calificaciones/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'calificaciones/signup.html', {'form': form})

# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')

@login_required
def dashboard(request):
    from django.db.models import Count, Max, Min

    total_calificaciones = Calificacion.objects.count()
    promedio_general = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']
    if promedio_general is not None:
        promedio_general = round(promedio_general, 2)

    aprobados = Calificacion.objects.filter(promedio__gte=60).count()
    reprobados = Calificacion.objects.filter(promedio__lt=60).count()

    mejores_estudiantes = Calificacion.objects.order_by('-promedio')[:5]
    ultimas_calificaciones = Calificacion.objects.order_by('-id')[:5]

    promedios_asignatura = (
        Calificacion.objects.values('asignatura')
        .annotate(promedio=Avg('promedio'), total=Count('id'))
        .order_by('-promedio')[:5]
    )

    promedios_asignatura = [
        {
            'asignatura': item['asignatura'],
            'promedio': round(item['promedio'], 2) if item['promedio'] is not None else None,
            'total': item['total'],
        }
        for item in promedios_asignatura
    ]

    return render(request, 'calificaciones/dashboard.html', {
        'total_calificaciones': total_calificaciones,
        'promedio_general': promedio_general,
        'aprobados': aprobados,
        'reprobados': reprobados,
        'mejores_estudiantes': mejores_estudiantes,
        'ultimas_calificaciones': ultimas_calificaciones,
        'promedios_asignatura': promedios_asignatura,
    })

@login_required
def estadisticas(request):
    from django.db.models import Count, Max, Min

    total_calificaciones = Calificacion.objects.count()
    promedio_general = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']
    if promedio_general is not None:
        promedio_general = round(promedio_general, 2)

    aprobados = Calificacion.objects.filter(promedio__gte=60).count()
    reprobados = Calificacion.objects.filter(promedio__lt=60).count()

    mejor_estudiante = Calificacion.objects.order_by('-promedio').first()
    peor_estudiante = Calificacion.objects.order_by('promedio').first()

    promedio_mas_alto = Calificacion.objects.aggregate(Max('promedio'))['promedio__max']
    promedio_mas_bajo = Calificacion.objects.aggregate(Min('promedio'))['promedio__min']

    if promedio_mas_alto is not None:
        promedio_mas_alto = round(promedio_mas_alto, 2)
    if promedio_mas_bajo is not None:
        promedio_mas_bajo = round(promedio_mas_bajo, 2)

    promedios_por_asignatura = (
        Calificacion.objects.values('asignatura')
        .annotate(promedio=Avg('promedio'), total=Count('id'))
        .order_by('-promedio')
    )

    promedios_por_asignatura = [
        {
            'asignatura': item['asignatura'],
            'promedio': round(item['promedio'], 2) if item['promedio'] is not None else None,
            'total': item['total'],
        }
        for item in promedios_por_asignatura
    ]

    return render(request, 'calificaciones/estadisticas.html', {
        'total_calificaciones': total_calificaciones,
        'promedio_general': promedio_general,
        'aprobados': aprobados,
        'reprobados': reprobados,
        'mejor_estudiante': mejor_estudiante,
        'peor_estudiante': peor_estudiante,
        'promedio_mas_alto': promedio_mas_alto,
        'promedio_mas_bajo': promedio_mas_bajo,
        'promedios_por_asignatura': promedios_por_asignatura,
    })

@login_required
def exportar_csv(request):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="calificaciones.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'nombre_estudiante',
        'identificacion',
        'asignatura',
        'nota1',
        'nota2',
        'nota3',
        'promedio',
    ])

    for c in Calificacion.objects.all().order_by('id'):
        writer.writerow([
            c.nombre_estudiante,
            c.identificacion,
            c.asignatura,
            c.nota1,
            c.nota2,
            c.nota3,
            c.promedio,
        ])

    return response

@login_required
def importar_csv(request):
    import csv
    from decimal import Decimal, InvalidOperation

    if request.method == 'POST':
        archivo = request.FILES.get('archivo_csv')
        if not archivo:
            messages.error(request, 'Selecciona un archivo CSV')
            return redirect('importar_csv')

        try:
            contenido = archivo.read().decode('utf-8-sig').splitlines()
        except UnicodeDecodeError:
            messages.error(request, 'No se pudo leer el archivo. Usa UTF-8')
            return redirect('importar_csv')

        lector = csv.reader(contenido)
        filas = list(lector)
        if not filas:
            messages.error(request, 'El archivo CSV está vacío')
            return redirect('importar_csv')

        creados = 0
        omitidos = 0
        errores = 0

        inicio = 1
        if filas and filas[0] and 'nombre' in filas[0][0].lower():
            inicio = 1
        else:
            inicio = 0

        for row in filas[inicio:]:
            if len(row) < 6:
                errores += 1
                continue

            nombre_estudiante, identificacion, asignatura, n1, n2, n3 = [c.strip() for c in row[:6]]
            if not (nombre_estudiante and identificacion and asignatura):
                errores += 1
                continue

            existe = Calificacion.objects.filter(
                identificacion=identificacion,
                asignatura=asignatura,
            ).exists()
            if existe:
                omitidos += 1
                continue

            try:
                nota1 = Decimal(n1)
                nota2 = Decimal(n2)
                nota3 = Decimal(n3)
            except (InvalidOperation, ValueError):
                errores += 1
                continue

            Calificacion.objects.create(
                nombre_estudiante=nombre_estudiante,
                identificacion=identificacion,
                asignatura=asignatura,
                nota1=nota1,
                nota2=nota2,
                nota3=nota3,
            )
            creados += 1

        if creados:
            messages.success(request, f'Se importaron {creados} registros')
        if omitidos:
            messages.info(request, f'Se omitieron {omitidos} registros duplicados')
        if errores:
            messages.warning(request, f'Hubo {errores} filas con errores')

        return redirect('listar_calificaciones')

    return render(request, 'calificaciones/importar_csv.html')


# CREAR
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


# LISTAR
@login_required
def listar_calificaciones(request):
    """Lista calificaciones con búsqueda, filtros y paginación"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Obtener todas las calificaciones
    calificaciones = Calificacion.objects.all()
    promedio_general = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']

    if promedio_general is not None:
        promedio_general = round(promedio_general, 2)

    return render(request, 'calificaciones/listar.html', {
        'calificaciones': calificaciones,
        'promedio_general': promedio_general
    })


# EDITAR
@login_required
def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada')
            return redirect('listar_calificaciones')
    else:
        form = CalificacionForm(instance=calificacion)

    return render(request, 'calificaciones/editar.html', {
        'form': form
    })


# ELIMINAR
@login_required
def eliminar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)

    if request.method == 'POST':
        calificacion.delete()
        messages.success(request, 'Calificación eliminada')
        return redirect('listar_calificaciones')

    return render(request, 'calificaciones/eliminar.html', {
        'calificacion': calificacion
    })


# PROMEDIO
@login_required
def promedio_general(request):
    promedio = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']

    if promedio:
        promedio = round(promedio, 2)

    return render(request, 'calificaciones/promedio_general.html', {
        'promedio': promedio
    })
