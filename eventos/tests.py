from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import datetime

from .models import Evento, TipoEvento, Ubicacion, Servicio
from .singleton import ConfiguracionGlobal
from .builder import EventoConferenciaBuilder, EventoBodaBuilder, DirectorEvento
from .prototype import EventoConcreto


class SingletonTestCase(TestCase):
    def test_singleton_unica_instancia(self):
        """Verificar que solo existe una instancia"""
        config1 = ConfiguracionGlobal()
        config2 = ConfiguracionGlobal()
        self.assertIs(config1, config2)
    
    def test_singleton_get_instance(self):
        """Verificar que get_instance retorna la misma instancia"""
        config1 = ConfiguracionGlobal.get_instance()
        config2 = ConfiguracionGlobal.get_instance()
        self.assertIs(config1, config2)
    
    def test_singleton_estado_compartido(self):
        """Verificar que el estado es compartido"""
        config1 = ConfiguracionGlobal.get_instance()
        config1.moneda = 'EUR'
        config2 = ConfiguracionGlobal.get_instance()
        self.assertEqual(config2.moneda, 'EUR')
        # Reset
        config1.moneda = 'USD'
    
    def test_singleton_actualizar_desde_dict(self):
        """Verificar actualización desde diccionario"""
        config = ConfiguracionGlobal.get_instance()
        config.update_from_dict({'impuestos': 15.0, 'limite_asistentes': 500})
        self.assertEqual(config.impuestos, 15.0)
        self.assertEqual(config.limite_asistentes, 500)
    
    def test_singleton_to_dict(self):
        """Verificar serialización a diccionario"""
        config = ConfiguracionGlobal.get_instance()
        d = config.to_dict()
        self.assertIn('moneda', d)
        self.assertIn('impuestos', d)
        self.assertIn('limite_asistentes', d)
        self.assertIn('notificaciones', d)
        self.assertIn('modo_mantenimiento', d)


class BuilderTestCase(TestCase):
    def test_conferencia_builder(self):
        """Construir una conferencia completa"""
        builder = EventoConferenciaBuilder()
        director = DirectorEvento(builder)
        evento = director.construir_conferencia_completa(
            nombre='Conferencia Tech',
            ubicacion='Centro de Convenciones',
            fecha='2025-06-01T10:00',
            capacidad=500,
            presupuesto=10000.0,
        )
        self.assertEqual(evento['nombre'], 'Conferencia Tech')
        self.assertEqual(evento['tipo'], 'conferencia')
        self.assertTrue(evento['escenario'])
        self.assertTrue(evento['streaming'])
        self.assertTrue(evento['seguridad'])
        self.assertTrue(evento['catering'])
    
    def test_boda_builder_sin_streaming(self):
        """Construir una boda sin streaming"""
        builder = EventoBodaBuilder()
        director = DirectorEvento(builder)
        evento = director.construir_boda_basica(
            nombre='Boda de Juan',
            ubicacion='Salon de Eventos',
            fecha='2025-07-15T18:00',
            capacidad=200,
            presupuesto=25000.0,
        )
        self.assertEqual(evento['tipo'], 'boda')
        self.assertFalse(evento['streaming'])
        self.assertTrue(evento['catering'])
        self.assertTrue(evento['decoracion'])
    
    def test_fluent_interface(self):
        """Verificar que el builder soporta encadenamiento de métodos"""
        builder = EventoConferenciaBuilder()
        resultado = (builder
                     .construir_configuracion_base()
                     .set_nombre('Test')
                     .set_capacidad(100)
                     .con_streaming()
                     .build())
        self.assertEqual(resultado['nombre'], 'Test')
        self.assertTrue(resultado['streaming'])
    
    def test_builder_reset_despues_de_build(self):
        """Verificar que el builder se resetea después de build"""
        builder = EventoConferenciaBuilder()
        builder.construir_configuracion_base().set_nombre('Evento 1')
        ev1 = builder.build()
        builder.construir_configuracion_base().set_nombre('Evento 2')
        ev2 = builder.build()
        self.assertEqual(ev1['nombre'], 'Evento 1')
        self.assertEqual(ev2['nombre'], 'Evento 2')


class PrototypeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass')
        self.tipo = TipoEvento.objects.create(nombre='Conferencia')
        self.ubicacion = Ubicacion.objects.create(
            nombre='Centro', direccion='Calle 1', ciudad='Madrid', capacidad_maxima=500
        )
    
    def test_clonar_evento(self):
        """Clonar un evento y verificar que es independiente"""
        evento_original = Evento.objects.create(
            nombre='Evento Original',
            tipo=self.tipo,
            fecha=timezone.now(),
            capacidad=100,
            presupuesto=5000,
            organizador=self.user,
        )
        clon = evento_original.clonar()
        self.assertNotEqual(evento_original.pk, clon.pk)
        self.assertTrue(clon.es_clon)
        self.assertEqual(clon.evento_original, evento_original)
    
    def test_clonar_no_afecta_original(self):
        """Modificar el clon no debe afectar al original"""
        evento_original = Evento.objects.create(
            nombre='Evento Original',
            tipo=self.tipo,
            fecha=timezone.now(),
            capacidad=100,
            presupuesto=5000,
            organizador=self.user,
        )
        clon = evento_original.clonar(nuevo_nombre='Clon Modificado')
        clon.capacidad = 999
        clon.save()
        
        evento_original.refresh_from_db()
        self.assertEqual(evento_original.capacidad, 100)
        self.assertEqual(clon.capacidad, 999)
    
    def test_clonar_multiples_veces(self):
        """Clonar un evento múltiples veces"""
        evento_original = Evento.objects.create(
            nombre='Evento Base',
            tipo=self.tipo,
            fecha=timezone.now(),
            capacidad=100,
            presupuesto=5000,
            organizador=self.user,
        )
        clones = [evento_original.clonar(nuevo_nombre=f'Clon {i}') for i in range(3)]
        self.assertEqual(len(clones), 3)
        for clon in clones:
            self.assertTrue(clon.es_clon)
    
    def test_prototype_python_clonar(self):
        """Test del patrón prototype con EventoConcreto"""
        datos = {'nombre': 'Evento A', 'capacidad': 100, 'streaming': True}
        proto = EventoConcreto(datos)
        clon = proto.clonar()
        
        clon.modificar(nombre='Evento B', capacidad=200)
        self.assertEqual(proto.datos['nombre'], 'Evento A')
        self.assertEqual(clon.datos['nombre'], 'Evento B')


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='testpass')
        self.tipo = TipoEvento.objects.create(nombre='Conferencia')
        self.ubicacion = Ubicacion.objects.create(
            nombre='Sala A', direccion='Calle 1', ciudad='Madrid', capacidad_maxima=500
        )
    
    def test_index_accessible(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass',
        })
        self.assertEqual(response.status_code, 302)
    
    def test_crear_evento_requiere_login(self):
        response = self.client.get(reverse('evento_crear'))
        self.assertEqual(response.status_code, 302)
    
    def test_crear_evento_autenticado(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('evento_crear'))
        self.assertEqual(response.status_code, 200)
    
    def test_clonar_evento_view(self):
        self.client.login(username='testuser', password='testpass')
        evento = Evento.objects.create(
            nombre='Evento Test',
            tipo=self.tipo,
            fecha=timezone.now(),
            capacidad=100,
            presupuesto=5000,
            organizador=self.user,
        )
        response = self.client.get(reverse('evento_clonar', args=[evento.pk]))
        self.assertEqual(response.status_code, 200)
