from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from ..models import Evento, TipoEvento, Ubicacion, Servicio
from .serializers import (EventoSerializer, TipoEventoSerializer, 
                           UbicacionSerializer, ServicioSerializer)
from ..singleton import ConfiguracionGlobal


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)
    
    @action(detail=True, methods=['post'])
    def clonar(self, request, pk=None):
        evento = self.get_object()
        nuevo_nombre = request.data.get('nombre', f'Copia de {evento.nombre}')
        nueva_fecha_str = request.data.get('fecha')
        nueva_fecha = None
        if nueva_fecha_str:
            from datetime import datetime
            try:
                nueva_fecha = datetime.fromisoformat(nueva_fecha_str)
            except ValueError:
                pass
        
        nuevo_evento = evento.clonar(
            nuevo_nombre=nuevo_nombre,
            nueva_fecha=nueva_fecha,
            organizador=request.user,
        )
        serializer = self.get_serializer(nuevo_evento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def configuracion_singleton(self, request):
        config = ConfiguracionGlobal.get_instance()
        return Response(config.to_dict())


class TipoEventoViewSet(viewsets.ModelViewSet):
    queryset = TipoEvento.objects.all()
    serializer_class = TipoEventoSerializer
    permission_classes = [IsAuthenticated]


class UbicacionViewSet(viewsets.ModelViewSet):
    queryset = Ubicacion.objects.all()
    serializer_class = UbicacionSerializer
    permission_classes = [IsAuthenticated]


class ServicioViewSet(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [IsAuthenticated]
