from tienda.models import Producto

class Carrito:
    def __init__(self, request):
        self.request = request  # Guardamos el request para acceder al usuario
        self.session = request.session
        carrito = self.session.get('session_key')
        if not carrito:
            carrito = self.session['session_key'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        cantidad = int(cantidad)
        
        if producto_id in self.carrito:
            self.carrito[producto_id] += cantidad
        else:
            self.carrito[producto_id] = cantidad
            
        self.guardar()

    def actualizar(self, producto, cantidad):
        producto_id = str(producto.id)
        cantidad = int(cantidad)
        
        if producto_id in self.carrito:
            if cantidad > 0:
                self.carrito[producto_id] = cantidad
            else:
                self.eliminar(producto)
            self.guardar()

    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def guardar(self):
        # 1. Marcamos la sesión como modificada para que Django la guarde
        self.session.modified = True
        
        # 2. Si el usuario está logueado, guardamos una copia exacta en la base de datos de inmediato
        if self.request.user.is_authenticated:
            self.request.user.carrito_guardado = self.carrito
            # Usamos update_fields para optimizar y guardar solo este campo
            self.request.user.save(update_fields=['carrito_guardado'])

    def __iter__(self):
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=producto_ids)
        
        for producto in productos:
            producto_id = str(producto.id)
            cantidad = self.carrito[producto_id]
            
            yield {
                'producto': producto,
                'precio': producto.precio,
                'cantidad': cantidad,
                'subtotal': producto.precio * cantidad
            }

    def __len__(self):
        return sum(item for item in self.carrito.values())

    def total(self):
        return sum(item['producto'].precio * item['cantidad'] for item in self)
