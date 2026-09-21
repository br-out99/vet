from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_mascotas, name='lista_mascotas'),
    path('crear/', views.crear_mascota, name='crear_mascota'),
    path('editar/<int:pk>/', views.editar_mascota, name='editar_mascota'),
    path('eliminar/<int:pk>/', views.eliminar_mascota, name='eliminar_mascota'),
    path('buscar/', views.buscar_mascota, name='buscar_mascota'),
    path('vacunas-mes/', views.vacunas_mes, name='vacunas_mes'),
    path('actualizar-vacunacion/<int:pk>/', views.actualizar_vacunacion, name='actualizar_vacunacion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
]

