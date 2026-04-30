from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Avg
from .models import Calificacion
from .forms import CalificacionForm


def inicio(request):
    if request.user.is_authenticated:
        return redirect('listar_calificaciones')
    return redirect('login')


# LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('listar_calificaciones')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('listar_calificaciones')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'calificaciones/login.html')


# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('login')


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
    calificaciones = Calificacion.objects.all()
    promedio = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']

    if promedio:
        promedio = round(promedio, 2)

    return render(request, 'calificaciones/listar.html', {
        'calificaciones': calificaciones,
        'promedio': promedio
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

    return render(request, 'calificaciones/eliminar.html')


# PROMEDIO
@login_required
def promedio_general(request):
    promedio = Calificacion.objects.aggregate(Avg('promedio'))['promedio__avg']

    if promedio:
        promedio = round(promedio, 2)

    return render(request, 'calificaciones/promedio_general.html', {
        'promedio': promedio
    })