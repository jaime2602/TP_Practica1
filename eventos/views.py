from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Evento, TipoEvento, Ubicacion, Servicio, ConfiguracionEvento
from .singleton import ConfiguracionGlobal
from .builder import EventoConferenciaBuilder, EventoBodaBuilder, DirectorEvento
from .forms import (EventoForm, ConfiguracionEventoForm, LoginForm, 
                    RegisterForm, ConfiguracionGlobalForm, ClonarEventoForm)


def index(request):
    config = ConfiguracionGlobal.get_instance()
    if config.modo_mantenimiento and not request.user.is_staff:
        return render(request, 'eventos/mantenimiento.html')
    
    eventos = Evento.objects.all()
    tipo_filter = request.GET.get('tipo')
    fecha_filter = request.GET.get('fecha')
    
    if tipo_filter:
        eventos = eventos.filter(tipo__id=tipo_filter)
    if fecha_filter:
        eventos = eventos.filter(fecha__date=fecha_filter)
    
    tipos = TipoEvento.objects.all()
    context = {
        'eventos': eventos,
        'tipos': tipos,
        'config': config,
    }
    return render(request, 'eventos/index.html', context)


@login_required
def evento_detalle(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    config = ConfiguracionGlobal.get_instance()
    return render(request, 'eventos/evento_detalle.html', {'evento': evento, 'config': config})


@login_required
def evento_crear(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.organizador = request.user
            evento.save()
            form.save_m2m()
            messages.success(request, 'Evento creado exitosamente.')
            return redirect('evento_detalle', pk=evento.pk)
    else:
        form = EventoForm()
    
    tipos = TipoEvento.objects.all()
    return render(request, 'eventos/evento_form.html', {
        'form': form, 
        'titulo': 'Crear Evento',
        'tipos': tipos,
    })


@login_required
def evento_editar(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento actualizado exitosamente.')
            return redirect('evento_detalle', pk=evento.pk)
    else:
        form = EventoForm(instance=evento)
    
    return render(request, 'eventos/evento_form.html', {
        'form': form, 
        'titulo': 'Editar Evento',
        'evento': evento,
    })


@login_required
def evento_eliminar(request, pk):
    evento = get_object_or_404(Evento, pk=pk, organizador=request.user)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento eliminado exitosamente.')
        return redirect('index')
    return render(request, 'eventos/evento_confirmar_eliminar.html', {'evento': evento})


@login_required
def evento_clonar(request, pk):
    evento_original = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = ClonarEventoForm(request.POST)
        if form.is_valid():
            nuevo_nombre = form.cleaned_data.get('nombre')
            nueva_fecha = form.cleaned_data.get('fecha')
            nuevo_evento = evento_original.clonar(
                nuevo_nombre=nuevo_nombre,
                nueva_fecha=nueva_fecha,
                organizador=request.user,
            )
            messages.success(request, f'Evento clonado exitosamente como "{nuevo_evento.nombre}".')
            return redirect('evento_detalle', pk=nuevo_evento.pk)
    else:
        form = ClonarEventoForm(initial={
            'nombre': f'Copia de {evento_original.nombre}',
            'fecha': evento_original.fecha,
        })
    
    return render(request, 'eventos/evento_clonar.html', {
        'form': form, 
        'evento_original': evento_original,
    })


@login_required
def evento_builder(request):
    """Build event step by step using Builder pattern"""
    if request.method == 'POST':
        tipo_builder = request.POST.get('tipo_builder', 'conferencia')
        nombre = request.POST.get('nombre', 'Nuevo Evento')
        ubicacion_id = request.POST.get('ubicacion')
        fecha = request.POST.get('fecha')
        capacidad = int(request.POST.get('capacidad', 0))
        presupuesto = float(request.POST.get('presupuesto', 0))
        
        if tipo_builder == 'conferencia':
            builder = EventoConferenciaBuilder()
        else:
            builder = EventoBodaBuilder()
        
        director = DirectorEvento(builder)
        datos_evento = director.construir_conferencia_completa(
            nombre=nombre,
            ubicacion=ubicacion_id,
            fecha=fecha,
            capacidad=capacidad,
            presupuesto=presupuesto,
        ) if tipo_builder == 'conferencia' else director.construir_boda_basica(
            nombre=nombre,
            ubicacion=ubicacion_id,
            fecha=fecha,
            capacidad=capacidad,
            presupuesto=presupuesto,
        )
        
        # Create the actual DB event
        tipo_evento, _ = TipoEvento.objects.get_or_create(nombre=datos_evento['tipo'].capitalize())
        ubicacion = None
        if ubicacion_id:
            try:
                ubicacion = Ubicacion.objects.get(pk=int(ubicacion_id))
            except (Ubicacion.DoesNotExist, ValueError):
                pass
        
        from datetime import datetime
        fecha_obj = None
        if fecha:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%dT%H:%M')
                from django.utils import timezone as tz
                if timezone.is_naive(fecha_obj):
                    fecha_obj = tz.make_aware(fecha_obj)
            except ValueError:
                fecha_obj = timezone.now()
        
        evento = Evento(
            nombre=datos_evento['nombre'],
            tipo=tipo_evento,
            descripcion=datos_evento.get('descripcion', ''),
            fecha=fecha_obj or timezone.now(),
            ubicacion=ubicacion,
            capacidad=datos_evento['capacidad'],
            presupuesto=datos_evento['presupuesto'],
            organizador=request.user,
            catering=datos_evento['catering'],
            escenario=datos_evento['escenario'],
            iluminacion=datos_evento['iluminacion'],
            seguridad=datos_evento['seguridad'],
            streaming=datos_evento['streaming'],
            decoracion=datos_evento['decoracion'],
        )
        evento.save()
        messages.success(request, f'Evento construido exitosamente usando Builder ({tipo_builder}).')
        return redirect('evento_detalle', pk=evento.pk)
    
    ubicaciones = Ubicacion.objects.all()
    return render(request, 'eventos/evento_builder.html', {'ubicaciones': ubicaciones})


@login_required
@user_passes_test(lambda u: u.is_staff)
def configuracion_global(request):
    config = ConfiguracionGlobal.get_instance()
    if request.method == 'POST':
        form = ConfiguracionGlobalForm(request.POST)
        if form.is_valid():
            config.update_from_dict(form.cleaned_data)
            messages.success(request, 'Configuración global actualizada.')
            return redirect('configuracion_global')
    else:
        form = ConfiguracionGlobalForm(initial=config.to_dict())
    
    return render(request, 'eventos/configuracion_global.html', {
        'form': form, 
        'config': config,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect(request.GET.get('next', 'index'))
            messages.error(request, 'Credenciales inválidas.')
    else:
        form = LoginForm()
    return render(request, 'eventos/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'eventos/register.html', {'form': form})
