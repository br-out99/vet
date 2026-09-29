from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date

from .models import Mascota


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================
def es_administrador(user):
    return user.is_superuser or user.is_staff


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

    especie_filtro = request.GET.get('especie', '').strip().lower()
    if especie_filtro:
        mascotas = mascotas.filter(especie__iexact=especie_filtro)

    context = {
        'mascotas': mascotas,
        'especies': Mascota.ESPECIE_CHOICES,
        'especie_seleccionada': especie_filtro,
        'es_admin': request.user.is_superuser or request.user.is_staff,
    }
    return render(request, 'mascotas/lista.html', context)


# ============================================================
# CREAR MASCOTA (solo admin) - CON VALIDACIÓN
# ============================================================
@login_required
def crear_mascota(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        especie = request.POST.get('especie', '').strip()
        edad = request.POST.get('edad', '').strip()
        estado_vacunacion = request.POST.get('estado_vacunacion', '').strip()
        fecha_ultima_vacuna = request.POST.get('fecha_ultima_vacuna', '').strip()

        errores = []

        if not nombre:
            errores.append('El nombre es obligatorio.')
        elif len(nombre) < 2:
            errores.append('El nombre debe tener al menos 2 caracteres.')
        elif len(nombre) > 100:
            errores.append('El nombre no puede tener más de 100 caracteres.')

        especies_validas = [c[0] for c in Mascota.ESPECIE_CHOICES]
        if not especie:
            errores.append('La especie es obligatoria.')
        elif especie not in especies_validas:
            errores.append('La especie seleccionada no es válida.')

        if not edad:
            errores.append('La edad es obligatoria.')
        else:
            try:
                edad_int = int(edad)
                if edad_int < 0:
                    errores.append('La edad no puede ser negativa.')
                elif edad_int > 50:
                    errores.append('La edad no puede ser mayor a 50 años.')
            except ValueError:
                errores.append('La edad debe ser un número entero.')

        estados_validos = [c[0] for c in Mascota.VACUNACION_CHOICES]
        if not estado_vacunacion:
            errores.append('El estado de vacunación es obligatorio.')
        elif estado_vacunacion not in estados_validos:
            errores.append('El estado de vacunación no es válido.')

        if fecha_ultima_vacuna:
            try:
                fecha_dt = date.fromisoformat(fecha_ultima_vacuna)
                if fecha_dt > date.today():
                    errores.append('La fecha de vacuna no puede ser futura.')
            except ValueError:
                errores.append('La fecha de vacuna no es válida.')

        if errores:
            return render(request, 'mascotas/crear.html', {
                'especies': Mascota.ESPECIE_CHOICES,
                'estados': Mascota.VACUNACION_CHOICES,
                'errores': errores,
                'datos': request.POST,
            })

        Mascota.objects.create(
            nombre=nombre,
            especie=especie,
            edad=int(edad),
            estado_vacunacion=estado_vacunacion,
            fecha_ultima_vacuna=fecha_ultima_vacuna if fecha_ultima_vacuna else None,
            veterinario=request.user
        )
        messages.success(request, f'¡Mascota {nombre} creada exitosamente!')
        return redirect('lista_mascotas')

    return render(request, 'mascotas/crear.html', {
        'especies': Mascota.ESPECIE_CHOICES,
        'estados': Mascota.VACUNACION_CHOICES,
    })


# ============================================================
# EDITAR MASCOTA (admin o dueño) - CON VALIDACIÓN
# ============================================================
@login_required
def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    if not (request.user.is_superuser or request.user.is_staff or mascota.veterinario == request.user):
        messages.error(request, 'No tienes permiso para editar esta mascota.')
        return redirect('lista_mascotas')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        especie = request.POST.get('especie', '').strip()
        edad = request.POST.get('edad', '').strip()
        estado_vacunacion = request.POST.get('estado_vacunacion', '').strip()
        fecha_ultima_vacuna = request.POST.get('fecha_ultima_vacuna', '').strip()

        errores = []

        if not nombre or len(nombre) < 2:
            errores.append('El nombre debe tener al menos 2 caracteres.')
        elif len(nombre) > 100:
            errores.append('El nombre no puede tener más de 100 caracteres.')

        especies_validas = [c[0] for c in Mascota.ESPECIE_CHOICES]
        if especie not in especies_validas:
            errores.append('La especie seleccionada no es válida.')

        try:
            edad_int = int(edad)
            if edad_int < 0 or edad_int > 50:
                errores.append('La edad debe estar entre 0 y 50 años.')
        except ValueError:
            errores.append('La edad debe ser un número entero.')

        estados_validos = [c[0] for c in Mascota.VACUNACION_CHOICES]
        if estado_vacunacion not in estados_validos:
            errores.append('El estado de vacunación no es válido.')

        if fecha_ultima_vacuna:
            try:
                fecha_dt = date.fromisoformat(fecha_ultima_vacuna)
                if fecha_dt > date.today():
                    errores.append('La fecha de vacuna no puede ser futura.')
            except ValueError:
                errores.append('La fecha de vacuna no es válida.')

        if errores:
            return render(request, 'mascotas/editar.html', {
                'mascota': mascota,
                'especies': Mascota.ESPECIE_CHOICES,
                'estados': Mascota.VACUNACION_CHOICES,
                'errores': errores,
                'datos': request.POST,
            })

        mascota.nombre = nombre
        mascota.especie = especie
        mascota.edad = int(edad)
        mascota.estado_vacunacion = estado_vacunacion
        mascota.fecha_ultima_vacuna = fecha_ultima_vacuna if fecha_ultima_vacuna else None
        mascota.save()

        messages.success(request, f'¡Mascota {mascota.nombre} actualizada!')
        return redirect('lista_mascotas')

    return render(request, 'mascotas/editar.html', {
        'mascota': mascota,
        'especies': Mascota.ESPECIE_CHOICES,
        'estados': Mascota.VACUNACION_CHOICES,
    })


# ============================================================
# ELIMINAR MASCOTA (admin o dueño)
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
# BUSCAR MASCOTA POR NOMBRE
# ============================================================
@login_required
def buscar_mascota(request):
    query = request.GET.get('q', '').strip()
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
# ACTUALIZAR ESTADO DE VACUNACIÓN (admin o dueño)
# ============================================================
@login_required
def actualizar_vacunacion(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)

    if not (request.user.is_superuser or request.user.is_staff or mascota.veterinario == request.user):
        messages.error(request, 'No tienes permiso para actualizar esta mascota.')
        return redirect('lista_mascotas')

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_vacunacion', '').strip()
        fecha_vacuna = request.POST.get('fecha_ultima_vacuna', '').strip()

        errores = []
        estados_validos = [c[0] for c in Mascota.VACUNACION_CHOICES]
        if nuevo_estado not in estados_validos:
            errores.append('El estado de vacunación no es válido.')

        if fecha_vacuna:
            try:
                fecha_dt = date.fromisoformat(fecha_vacuna)
                if fecha_dt > date.today():
                    errores.append('La fecha de vacuna no puede ser futura.')
            except ValueError:
                errores.append('La fecha de vacuna no es válida.')

        if errores:
            return render(request, 'mascotas/actualizar_vacunacion.html', {
                'mascota': mascota,
                'estados': Mascota.VACUNACION_CHOICES,
                'errores': errores,
            })

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