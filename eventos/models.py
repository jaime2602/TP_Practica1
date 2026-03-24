from django.db import models
from django.contrib.auth.models import User
import copy


class TipoEvento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Evento'
    
    def __str__(self):
        return self.nombre


class Ubicacion(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    capacidad_maxima = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'
    
    def __str__(self):
        return f"{self.nombre} - {self.ciudad}"


class Servicio(models.Model):
    TIPO_CHOICES = [
        ('catering', 'Catering'),
        ('escenario', 'Escenario'),
        ('iluminacion', 'Iluminación'),
        ('seguridad', 'Seguridad'),
        ('streaming', 'Streaming'),
        ('decoracion', 'Decoración'),
        ('otro', 'Otro'),
    ]
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class Evento(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo = models.ForeignKey(TipoEvento, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    capacidad = models.IntegerField(default=0)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    servicios = models.ManyToManyField(Servicio, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    organizador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    es_clon = models.BooleanField(default=False)
    evento_original = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Builder fields
    catering = models.BooleanField(default=False)
    escenario = models.BooleanField(default=False)
    iluminacion = models.BooleanField(default=False)
    seguridad = models.BooleanField(default=False)
    streaming = models.BooleanField(default=False)
    decoracion = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def clonar(self, nuevo_nombre=None, nueva_fecha=None, organizador=None):
        """Prototype pattern: clone the event"""
        servicios_originales = list(self.servicios.all())
        
        nuevo_evento = Evento(
            nombre=nuevo_nombre or f"Copia de {self.nombre}",
            tipo=self.tipo,
            descripcion=self.descripcion,
            fecha=nueva_fecha or self.fecha,
            fecha_fin=self.fecha_fin,
            ubicacion=self.ubicacion,
            capacidad=self.capacidad,
            presupuesto=self.presupuesto,
            estado='borrador',
            organizador=organizador or self.organizador,
            es_clon=True,
            evento_original=self,
            catering=self.catering,
            escenario=self.escenario,
            iluminacion=self.iluminacion,
            seguridad=self.seguridad,
            streaming=self.streaming,
            decoracion=self.decoracion,
        )
        nuevo_evento.save()
        nuevo_evento.servicios.set(servicios_originales)
        return nuevo_evento


class ConfiguracionEvento(models.Model):
    evento = models.OneToOneField(Evento, on_delete=models.CASCADE, related_name='configuracion')
    notas_internas = models.TextField(blank=True)
    requerimientos_especiales = models.TextField(blank=True)
    contacto_proveedor = models.CharField(max_length=200, blank=True)
    fecha_limite_inscripcion = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Configuración de Evento'
        verbose_name_plural = 'Configuraciones de Evento'
    
    def __str__(self):
        return f"Config: {self.evento.nombre}"
