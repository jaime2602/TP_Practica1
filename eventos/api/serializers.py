from rest_framework import serializers
from ..models import Evento, TipoEvento, Ubicacion, Servicio, ConfiguracionEvento


class TipoEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEvento
        fields = '__all__'


class UbicacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ubicacion
        fields = '__all__'


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'


class ConfiguracionEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionEvento
        fields = '__all__'


class EventoSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    organizador_username = serializers.CharField(source='organizador.username', read_only=True)
    servicios_detalle = ServicioSerializer(source='servicios', many=True, read_only=True)
    
    class Meta:
        model = Evento
        fields = '__all__'
        read_only_fields = ['organizador', 'fecha_creacion', 'fecha_modificacion']
