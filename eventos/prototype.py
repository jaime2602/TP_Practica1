import copy
from abc import ABC, abstractmethod


class EventoPrototype(ABC):
    @abstractmethod
    def clonar(self):
        pass


class EventoConcreto(EventoPrototype):
    def __init__(self, datos):
        self.datos = copy.deepcopy(datos)
    
    def clonar(self):
        nuevo = EventoConcreto(copy.deepcopy(self.datos))
        return nuevo
    
    def modificar(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.datos:
                self.datos[key] = value
        return self
