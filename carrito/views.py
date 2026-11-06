from django.shortcuts import render, get_object_or_404
from .carrito import Carrito
from tienda.models import Producto
from django.http import JsonResponse

def carrito_detalle(request):
    # Instanciamos el carrito. Como tiene __iter__, podemos recorrerlo directamente en el HTML
    carrito = Carrito(request)
    return render(request, 'carrito/carrito_detalle.html', {'carrito': carrito})

def carrito_agregar(request):
    carrito = Carrito(request)
    
    if request.POST.get('action') == 'post':
        producto_id = int(request.POST.get('producto_id'))
        cantidad = int(request.POST.get('cantidad', 1))
        
        producto = get_object_or_404(Producto, id=producto_id)
        carrito.agregar(producto=producto, cantidad=cantidad)
        
        cantidad_carrito = len(carrito)
        return JsonResponse({'cantidad': cantidad_carrito, 'nombre': producto.nombre})

def carrito_borrar(request):
    carrito = Carrito(request)
    
    if request.POST.get('action') == 'post':
        producto_id = int(request.POST.get('producto_id'))
        producto = get_object_or_404(Producto, id=producto_id)
        
        carrito.eliminar(producto=producto)
        
        return JsonResponse({
            'cantidad': len(carrito),
            'total': carrito.total()
        })

def carrito_actualizar(request):
    carrito = Carrito(request)
    
    if request.POST.get('action') == 'post':
        producto_id = int(request.POST.get('producto_id'))
        cantidad = int(request.POST.get('cantidad'))
        
        producto = get_object_or_404(Producto, id=producto_id)
        carrito.actualizar(producto=producto, cantidad=cantidad)
        
        return JsonResponse({
            'cantidad': len(carrito),
            'total': carrito.total()
        })