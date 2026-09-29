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
# FUNCIÓN AUXILIAR: Obtener mascotas visibles para el usuario
# Admin ve todas, veterinario solo las suyas
# ============================================================
def mascotas_visibles_para(user):
    if user.is_superuser or user.is_staff:
        return Mascota.objects.all()
    return Mascota.objects.filter(veterinario=user)


# ============================================================
# LISTA DE MASCOTAS
# ============================================================
@login_required
def lista_mascotas(request):
    mascotas = mascotas_visibles_para(request.user).order_by('nombre')

    # Filtrar por especie
    especie_filtro = request.GET.get('especie', '').strip().lower()
    if especie_filtro:
        mascotas = mascotas.filter(especie__iexact=especie_filtro)

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
                fecha_ultima_vacuna=fecha_ultima_vacuna if fecha_ultima_vacuna else None,
                veterinario=request.user  # <-- asigna el usuario actual
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
# EDITAR MASCOTA (solo admin o dueño de la mascota)
# ============================================================
@login_required
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    # Verificar permiso: admin o dueño
    if not (request.user.is_superuser or request.user.is_staff or mascota.veterinario == request.user):
        messages.error(request, 'No tienes permiso para editar esta mascota.')
        return redirect('lista_mascotas')

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
# ELIMINAR MASCOTA (solo admin o dueño)
# ============================================================
@login_required
def eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    if not (request.user.is_superuser or request.user.is_staff or mascota.veterinario == request.user):
        messages.error(request, 'No tienes permiso para eliminar esta mascota.')
        return redirect('lista_mascotas')

    nombre = mascota.nombre

    if request.method == 'POST':
        mascota.delete()
        messages.success(request, f'¡Mascota {nombre} eliminada!')
        return redirect('lista_mascotas')

    return render(request, 'mascotas/eliminar.html', {'mascota': mascota})


# ============================================================
# BUSCAR MASCOTA POR NOMBRE (solo las visibles)
# ============================================================
@login_required
def buscar_mascota(request):
    query = request.GET.get('q', '')
    mascotas = []
    if query:
        mascotas = mascotas_visibles_para(request.user).filter(nombre__icontains=query)

    return render(request, 'mascotas/buscar.html', {
        'mascotas': mascotas,
        'query': query
    })


# ============================================================
# MASCOTAS QUE NECESITAN VACUNA ESTE MES
# ============================================================
@login_required
def vacunas_mes(request):
    mascotas = mascotas_visibles_para(request.user).filter(estado_vacunacion='pendiente')
    mascotas_necesitan = [m for m in mascotas if m.necesita_vacuna_este_mes()]

    return render(request, 'mascotas/vacunas_mes.html', {
        'mascotas': mascotas_necesitan
    })


# ============================================================
# ACTUALIZAR ESTADO DE VACUNACIÓN (solo admin o dueño)
# ============================================================
@login_required
def actualizar_vacunacion(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    if not (request.user.is_superuser or request.user.is_staff or mascota.veterinario == request.user):
        messages.error(request, 'No tienes permiso para actualizar esta mascota.')
        return redirect('lista_mascotas')

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
# INICIAR SESIÓN
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