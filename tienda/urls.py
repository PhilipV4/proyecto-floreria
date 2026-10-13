from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),

    #productos
    path('productos/', views.lista_productos, name='lista_productos'),
    #admin
    path('gestion/', views.admin_lista_productos, name='admin_lista_productos'),
    path('gestion/crear/', views.crear_producto, name='crear_producto'),
    path('gestion/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('gestion/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('gestion/crear_categoria/', views.crear_categoria, name='crear_categoria'),
    path('gestion/crear_ocasion/', views.crear_ocasion, name='crear_ocasion'),

    #PRUEBA
    path('prueba/', views.prueba, name='prueba'),

    #PRUEBA NAVBAR Y FOOTER
    path('componentes/', views.prueba_global_componentes, name='prueba_global_componentes'),

    #PRUEBA DETALLE PRODUCTO
    path('detalle_producto/', views.detalle_producto, name='detalle_producto'),
]