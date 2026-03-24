from abc import ABC, abstractmethod
import copy

class EventoBuilder(ABC):
    def __init__(self):
        self.reset()
    
    def reset(self):
        self._evento = {
            'nombre': '',
            'tipo': '',
            'ubicacion': '',
            'fecha': None,
            'capacidad': 0,
            'catering': False,
            'escenario': False,
            'iluminacion': False,
            'seguridad': False,
            'streaming': False,
            'decoracion': False,
            'servicios_adicionales': [],
            'presupuesto': 0.0,
            'descripcion': '',
        }
    
    def set_nombre(self, nombre):
        self._evento['nombre'] = nombre
        return self
    
    def set_ubicacion(self, ubicacion):
        self._evento['ubicacion'] = ubicacion
        return self
    
    def set_fecha(self, fecha):
        self._evento['fecha'] = fecha
        return self
    
    def set_capacidad(self, capacidad):
        self._evento['capacidad'] = capacidad
        return self
    
    def set_presupuesto(self, presupuesto):
        self._evento['presupuesto'] = presupuesto
        return self
    
    def set_descripcion(self, descripcion):
        self._evento['descripcion'] = descripcion
        return self
    
    def con_catering(self, valor=True):
        self._evento['catering'] = valor
        return self
    
    def con_escenario(self, valor=True):
        self._evento['escenario'] = valor
        return self
    
    def con_iluminacion(self, valor=True):
        self._evento['iluminacion'] = valor
        return self
    
    def con_seguridad(self, valor=True):
        self._evento['seguridad'] = valor
        return self
    
    def con_streaming(self, valor=True):
        self._evento['streaming'] = valor
        return self
    
    def con_decoracion(self, valor=True):
        self._evento['decoracion'] = valor
        return self
    
    def agregar_servicio(self, servicio):
        self._evento['servicios_adicionales'].append(servicio)
        return self
    
    @abstractmethod
    def construir_configuracion_base(self):
        pass
    
    def build(self):
        resultado = copy.deepcopy(self._evento)
        self.reset()
        return resultado


class EventoConferenciaBuilder(EventoBuilder):
    def construir_configuracion_base(self):
        self._evento['tipo'] = 'conferencia'
        self._evento['escenario'] = True
        self._evento['iluminacion'] = True
        self._evento['seguridad'] = True
        self._evento['streaming'] = True
        return self


class EventoBodaBuilder(EventoBuilder):
    def construir_configuracion_base(self):
        self._evento['tipo'] = 'boda'
        self._evento['catering'] = True
        self._evento['decoracion'] = True
        self._evento['iluminacion'] = True
        self._evento['seguridad'] = True
        return self


class DirectorEvento:
    def __init__(self, builder: EventoBuilder):
        self._builder = builder
    
    def set_builder(self, builder: EventoBuilder):
        self._builder = builder
    
    def construir_conferencia_completa(self, nombre, ubicacion, fecha, capacidad, presupuesto):
        return (self._builder
                .construir_configuracion_base()
                .set_nombre(nombre)
                .set_ubicacion(ubicacion)
                .set_fecha(fecha)
                .set_capacidad(capacidad)
                .set_presupuesto(presupuesto)
                .con_catering()
                .build())
    
    def construir_boda_basica(self, nombre, ubicacion, fecha, capacidad, presupuesto):
        return (self._builder
                .construir_configuracion_base()
                .set_nombre(nombre)
                .set_ubicacion(ubicacion)
                .set_fecha(fecha)
                .set_capacidad(capacidad)
                .set_presupuesto(presupuesto)
                .build())
