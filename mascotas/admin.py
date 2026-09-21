from django.contrib import admin
from .models import Mascota

class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'edad', 'estado_vacunacion', 'fecha_ultima_vacuna')
    list_filter = ('especie', 'estado_vacunacion')
    search_fields = ('nombre',)
    ordering = ('nombre',)
    list_editable = ('estado_vacunacion', 'fecha_ultima_vacuna')
    
admin.site.register(Mascota, MascotaAdmin)

# Register your models here.
