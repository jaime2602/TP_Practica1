from django.contrib import admin
from .models import Evento, TipoEvento, Ubicacion, Servicio, ConfiguracionEvento


@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ciudad', 'capacidad_maxima']
    search_fields = ['nombre', 'ciudad']


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'precio']
    list_filter = ['tipo']
    search_fields = ['nombre']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'fecha', 'estado', 'organizador', 'es_clon']
    list_filter = ['tipo', 'estado', 'es_clon']
    search_fields = ['nombre', 'descripcion']
    date_hierarchy = 'fecha'
    filter_horizontal = ['servicios']


@admin.register(ConfiguracionEvento)
class ConfiguracionEventoAdmin(admin.ModelAdmin):
    list_display = ['evento', 'contacto_proveedor', 'fecha_limite_inscripcion']
