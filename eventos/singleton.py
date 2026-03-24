class ConfiguracionGlobal:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._moneda = 'USD'
        self._impuestos = 21.0
        self._limite_asistentes = 10000
        self._notificaciones = True
        self._modo_mantenimiento = False
        self._initialized = True
    
    @classmethod
    def get_instance(cls):
        return cls()
    
    @property
    def moneda(self):
        return self._moneda
    
    @moneda.setter
    def moneda(self, value):
        self._moneda = value
    
    @property
    def impuestos(self):
        return self._impuestos
    
    @impuestos.setter
    def impuestos(self, value):
        self._impuestos = float(value)
    
    @property
    def limite_asistentes(self):
        return self._limite_asistentes
    
    @limite_asistentes.setter
    def limite_asistentes(self, value):
        self._limite_asistentes = int(value)
    
    @property
    def notificaciones(self):
        return self._notificaciones
    
    @notificaciones.setter
    def notificaciones(self, value):
        self._notificaciones = bool(value)
    
    @property
    def modo_mantenimiento(self):
        return self._modo_mantenimiento
    
    @modo_mantenimiento.setter
    def modo_mantenimiento(self, value):
        self._modo_mantenimiento = bool(value)
    
    def to_dict(self):
        return {
            'moneda': self._moneda,
            'impuestos': self._impuestos,
            'limite_asistentes': self._limite_asistentes,
            'notificaciones': self._notificaciones,
            'modo_mantenimiento': self._modo_mantenimiento,
        }
    
    def update_from_dict(self, data):
        if 'moneda' in data:
            self.moneda = data['moneda']
        if 'impuestos' in data:
            self.impuestos = data['impuestos']
        if 'limite_asistentes' in data:
            self.limite_asistentes = data['limite_asistentes']
        if 'notificaciones' in data:
            self.notificaciones = data['notificaciones']
        if 'modo_mantenimiento' in data:
            self.modo_mantenimiento = data['modo_mantenimiento']
