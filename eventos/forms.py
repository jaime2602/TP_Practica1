from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Evento, ConfiguracionEvento


class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'nombre', 'tipo', 'descripcion', 'fecha', 'fecha_fin',
            'ubicacion', 'capacidad', 'presupuesto', 'servicios', 'estado',
            'catering', 'escenario', 'iluminacion', 'seguridad', 'streaming', 'decoracion',
        ]
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['fecha_fin'].input_formats = ['%Y-%m-%dT%H:%M']


class ConfiguracionEventoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionEvento
        fields = ['notas_internas', 'requerimientos_especiales', 'contacto_proveedor', 'fecha_limite_inscripcion']
        widgets = {
            'fecha_limite_inscripcion': forms.DateInput(attrs={'type': 'date'}),
        }


class ConfiguracionGlobalForm(forms.Form):
    MONEDA_CHOICES = [
        ('USD', 'USD - Dólar'),
        ('EUR', 'EUR - Euro'),
        ('ARS', 'ARS - Peso Argentino'),
    ]
    moneda = forms.ChoiceField(choices=MONEDA_CHOICES, label='Moneda')
    impuestos = forms.FloatField(min_value=0, max_value=100, label='Porcentaje de Impuestos (%)')
    limite_asistentes = forms.IntegerField(min_value=1, label='Límite máximo de asistentes')
    notificaciones = forms.BooleanField(required=False, label='Activar notificaciones')
    modo_mantenimiento = forms.BooleanField(required=False, label='Modo mantenimiento')


class ClonarEventoForm(forms.Form):
    nombre = forms.CharField(max_length=200, label='Nombre del nuevo evento')
    fecha = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M'],
        label='Nueva fecha',
    )
