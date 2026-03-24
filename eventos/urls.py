from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('eventos/<int:pk>/', views.evento_detalle, name='evento_detalle'),
    path('eventos/crear/', views.evento_crear, name='evento_crear'),
    path('eventos/<int:pk>/editar/', views.evento_editar, name='evento_editar'),
    path('eventos/<int:pk>/eliminar/', views.evento_eliminar, name='evento_eliminar'),
    path('eventos/<int:pk>/clonar/', views.evento_clonar, name='evento_clonar'),
    path('eventos/builder/', views.evento_builder, name='evento_builder'),
    path('configuracion/', views.configuracion_global, name='configuracion_global'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
