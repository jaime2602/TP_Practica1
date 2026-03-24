from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'eventos', views.EventoViewSet)
router.register(r'tipos', views.TipoEventoViewSet)
router.register(r'ubicaciones', views.UbicacionViewSet)
router.register(r'servicios', views.ServicioViewSet)

urlpatterns = router.urls
