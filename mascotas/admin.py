from django.contrib import admin
from django.utils import timezone
from .models import Mascota


@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    # Columnas que se muestran en la lista
    list_display = (
        'nombre',
        'especie',
        'edad',
        'veterinario',
        'estado_vacunacion',
        'proxima_vacuna_display',
        'fecha_ultima_vacuna',
    )

    # Filtros laterales
    list_filter = ('especie', 'estado_vacunacion', 'veterinario')

    # Búsqueda
    search_fields = ('nombre', 'veterinario__username')

    # Orden por defecto
    ordering = ('nombre',)

    # Campos editables directamente desde la lista
    list_editable = ('estado_vacunacion', 'fecha_ultima_vacuna')

    # Paginación
    list_per_page = 20

    # Campos de solo lectura
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    # Organización del formulario por secciones
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'especie', 'edad', 'veterinario')
        }),
        ('Vacunación', {
            'fields': ('estado_vacunacion', 'fecha_ultima_vacuna')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    def proxima_vacuna_display(self, obj):
        """Muestra si la mascota necesita vacuna este mes"""
        if obj.necesita_vacuna_este_mes():
            return "⚠️ SÍ"
        return "✅ No"
    proxima_vacuna_display.short_description = "¿Vacuna este mes?"

    # Personalizar el título de la columna veterinario
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Los no-admin solo ven sus propias mascotas
        if not (request.user.is_superuser or request.user.is_staff):
            qs = qs.filter(veterinario=request.user)
        return qs
    