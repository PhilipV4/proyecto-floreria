from django.urls import path
from . import views

urlpatterns = [

    path('', views.carrito_detalle, name='carrito_detalle'),
    path('agregar/', views.carrito_agregar, name='carrito_agregar'),
    path('borrar/', views.carrito_borrar, name='carrito_borrar'),
    path('actualizar/', views.carrito_actualizar, name='carrito_actualizar'),

]