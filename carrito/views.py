from django.shortcuts import render, get_object_or_404
from .carrito import Carrito
from tienda.models import Producto
from django.http import JsonResponse
# Create your views here.

def carrito_detalle(request):
    #obtener carrito
    carrito = Carrito(request)
    carrito_productos = carrito.get_productos()

    return render(request, 'carrito/carrito_detalle.html', {'carrito_productos': carrito_productos})

def carrito_agregar(request):
    # Obtener carrito
    carrito = Carrito(request)
    
    # Test POST
    if request.POST.get('action') == 'post':
        # Obtener producto ID
        producto_id = int(request.POST.get('producto_id'))
        # Obtener cantidad (si viene del detalle usa esa, si viene del catálogo por defecto es 1)
        cantidad = int(request.POST.get('cantidad', 1))
        # Buscar producto en la base de datos
        producto = get_object_or_404(Producto, id=producto_id)  
        # Guardar producto en la sesión con su cantidad
        carrito.agregar(producto=producto, cantidad=cantidad)
        # Obtener cantidad total de elementos en el carrito
        cantidad_carrito = len(carrito)
        # Devolver respuesta JSON
        response = JsonResponse({'cantidad': cantidad_carrito, 'nombre': producto.nombre})
        return response
    

def carrito_borrar(request):
    pass

def carrito_actualizar(request):
    pass


