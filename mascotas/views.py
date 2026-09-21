from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from datetime import date

from .models import Mascota


# ============================================================
# FUNCIÓN AUXILIAR: Verificar si el usuario es administrador
# ============================================================
def es_administrador(user):
    return user.is_superuser or user.is_staff


# ============================================================
# LISTA DE MASCOTAS (todos los usuarios autenticados pueden ver)
# ============================================================
# ============================================================
# LISTA DE MASCOTAS (todos los usuarios autenticados pueden ver)
# ============================================================
@login_required
def lista_mascotas(request):
    mascotas = Mascota.objects.all().order_by('nombre')

    # Filtrar por especie si se envía por GET
    especie_filtro = request.GET.get('especie', '').strip().lower()
    if especie_filtro:
        mascotas = mascotas.filter(especie__iexact=especie_filtro)

    # Usar DIRECTAMENTE las opciones del modelo (fijas y sin duplicados)
    especies = Mascota.ESPECIE_CHOICES

    context = {
        'mascotas': mascotas,
        'especies': especies,
        'especie_seleccionada': especie_filtro,
        'es_admin': request.user.is_superuser or request.user.is_staff,
    }
    return render(request, 'mascotas/lista.html', context)

# ============================================================
# CREAR MASCOTA (solo administradores)
# ============================================================
@login_required
@user_passes_test(es_administrador)
def crear_mascota(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        especie = request.POST.get('especie')
        edad = request.POST.get('edad')
        estado_vacunacion = request.POST.get('estado_vacunacion')
        fecha_ultima_vacuna = request.POST.get('fecha_ultima_vacuna')

        if nombre and especie and edad:
            Mascota.objects.create(
                nombre=nombre,
                especie=especie,
                edad=edad,
                estado_vacunacion=estado_vacunacion,
                fecha_ultima_vacuna=fecha_ultima_vacuna if fecha_ultima_vacuna else None
            )
            messages.success(request, f'¡Mascota {nombre} creada exitosamente!')
            return redirect('lista_mascotas')
        else:
            messages.error(request, 'Por favor complete todos los campos obligatorios')

    return render(request, 'mascotas/crear.html', {
        'especies': Mascota.ESPECIE_CHOICES,
        'estados': Mascota.VACUNACION_CHOICES,
    })


# ============================================================
# EDITAR MASCOTA (solo administradores)
# ============================================================
@login_required
@user_passes_test(es_administrador)
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    if request.method == 'POST':
        mascota.nombre = request.POST.get('nombre')
        mascota.especie = request.POST.get('especie')
        mascota.edad = request.POST.get('edad')
        mascota.estado_vacunacion = request.POST.get('estado_vacunacion')
        mascota.fecha_ultima_vacuna = request.POST.get('fecha_ultima_vacuna') or None
        mascota.save()

        messages.success(request, f'¡Mascota {mascota.nombre} actualizada!')
        return redirect('lista_mascotas')

    return render(request, 'mascotas/editar.html', {
        'mascota': mascota,
        'especies': Mascota.ESPECIE_CHOICES,
        'estados': Mascota.VACUNACION_CHOICES,
    })


# ============================================================
# ELIMINAR MASCOTA (solo administradores)
# ============================================================
@login_required
@user_passes_test(es_administrador)
def eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    nombre = mascota.nombre

    if request.method == 'POST':
        mascota.delete()
        messages.success(request, f'¡Mascota {nombre} eliminada!')
        return redirect('lista_mascotas')

    return render(request, 'mascotas/eliminar.html', {'mascota': mascota})


# ============================================================
# BUSCAR MASCOTA POR NOMBRE
# ============================================================
@login_required
def buscar_mascota(request):
    query = request.GET.get('q', '')
    mascotas = []
    if query:
        mascotas = Mascota.objects.filter(nombre__icontains=query)

    return render(request, 'mascotas/buscar.html', {
        'mascotas': mascotas,
        'query': query
    })


# ============================================================
# MASCOTAS QUE NECESITAN VACUNA ESTE MES
# ============================================================
@login_required
def vacunas_mes(request):
    mascotas = Mascota.objects.filter(estado_vacunacion='pendiente')
    # Filtrar las que realmente necesitan vacuna este mes
    mascotas_necesitan = [m for m in mascotas if m.necesita_vacuna_este_mes()]

    return render(request, 'mascotas/vacunas_mes.html', {
        'mascotas': mascotas_necesitan
    })


# ============================================================
# ACTUALIZAR ESTADO DE VACUNACIÓN (solo administradores)
# ============================================================
@login_required
@user_passes_test(es_administrador)
def actualizar_vacunacion(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_vacunacion')
        fecha_vacuna = request.POST.get('fecha_ultima_vacuna')

        if nuevo_estado:
            mascota.estado_vacunacion = nuevo_estado
            if fecha_vacuna:
                mascota.fecha_ultima_vacuna = fecha_vacuna
            mascota.save()
            messages.success(request, f'¡Estado de vacunación de {mascota.nombre} actualizado!')
            return redirect('lista_mascotas')

    return render(request, 'mascotas/actualizar_vacunacion.html', {
        'mascota': mascota,
        'estados': Mascota.VACUNACION_CHOICES
    })



# ============================================================
# INICIAR SESIÓN (para todos los usuarios)
# ============================================================
def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('lista_mascotas')
    else:
        form = AuthenticationForm()
    return render(request, 'mascotas/login.html', {'form': form})


# ============================================================
# CERRAR SESIÓN
# ============================================================
def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar_sesion')