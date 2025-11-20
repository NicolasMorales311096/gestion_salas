from django.contrib import admin
from .models import Sala, Reserva, RegistroAcceso


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad_maxima', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('rut', 'sala', 'hora_inicio', 'hora_fin')
    list_filter = ('sala', 'hora_inicio')
    search_fields = ('rut', 'sala__nombre')


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    list_display = ('fecha_hora', 'tipo_usuario', 'accion', 'username', 'rut', 'carrera', 'detalle')
    list_filter = ('tipo_usuario', 'accion', 'fecha_hora')
    search_fields = ('username', 'rut', 'carrera', 'detalle')
    ordering = ('-fecha_hora',)
