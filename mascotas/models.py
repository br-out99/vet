from django.db import models
from django.utils import timezone
from datetime import date

class Mascota(models.Model):
    # Opciones para especie
    ESPECIE_CHOICES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('conejo', 'Conejo'),
        ('loro', 'Loro'),
        ('hamster', 'Hámster'),
        ('pez', 'Pez'),
        ('otro', 'Otro'),
    ]
    
    # Opciones para estado de vacunación
    VACUNACION_CHOICES = [
        ('al_dia', '✅ Al día con vacunas'),
        ('pendiente', '⚠️ Pendiente de vacunas'),
        ('alergia', '🔶 Alergia a vacunas'),
    ]
    
    nombre = models.CharField(max_length=100, help_text="Nombre de la mascota")
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES, default='perro')
    edad = models.PositiveIntegerField(help_text="Edad en años")
    estado_vacunacion = models.CharField(
        max_length=20, 
        choices=VACUNACION_CHOICES, 
        default='pendiente'
    )
    fecha_ultima_vacuna = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()})"
    
    def necesita_vacuna_este_mes(self):
        """Verifica si la mascota necesita vacuna este mes"""
        if self.estado_vacunacion == 'al_dia':
            return False
        if not self.fecha_ultima_vacuna:
            return self.estado_vacunacion == 'pendiente'
        
        # Si la última vacuna fue hace más de 11 meses
        hoy = date.today()
        meses = (hoy.year - self.fecha_ultima_vacuna.year) * 12 + (hoy.month - self.fecha_ultima_vacuna.month)
        return meses >= 11 and self.estado_vacunacion == 'pendiente'
    
    def esta_vacunado(self):
        """Retorna True si está al día"""
        return self.estado_vacunacion == 'al_dia'
    
    def get_color_estado(self):
        """Retorna el color CSS según el estado"""
        colores = {
            'al_dia': 'green',
            'pendiente': 'red',
            'alergia': 'yellow'
        }
        return colores.get(self.estado_vacunacion, 'gray')
# Create your models here.
