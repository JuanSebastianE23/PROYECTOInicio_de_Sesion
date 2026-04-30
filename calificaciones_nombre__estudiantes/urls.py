from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('calificaciones/', views.listar_calificaciones, name='listar_calificaciones'),
    path('calificaciones/crear/', views.crear_calificacion, name='crear_calificacion'),
    path('calificaciones/editar/<int:pk>/', views.editar_calificacion, name='editar_calificacion'),
    path('calificaciones/eliminar/<int:pk>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    path('promedio-general/', views.promedio_general, name='promedio_general'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),
    path('importar-csv/', views.importar_csv, name='importar_csv'),
]
