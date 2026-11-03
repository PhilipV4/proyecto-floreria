from tienda.models import Producto

class Carrito():
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('session_key')
        if not carrito:
            carrito = self.session['session_key'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        cantidad = int(cantidad)
        
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'precio': str(producto.precio),
                'cantidad': cantidad
            }
        else:
            self.carrito[producto_id]['cantidad'] += cantidad
            
        self.guardar()

    def guardar(self):
        self.session.modified = True

    def __len__(self):
        return sum(item['cantidad'] for item in self.carrito.values())

    def get_productos(self):
        #obtener id de los productos del carrito
        productos_ids = self.carrito.keys()
        #usar los ids para obtener los productos
        productos = Producto.objects.filter(id__in=productos_ids)
        #devolver los productos
        return productos

    def __iter__(self):
        producto_ids = self.carrito.keys()
        productos = Producto.objects.filter(id__in=producto_ids)
        
        carrito_copia = self.carrito.copy()
        for producto in productos:
            carrito_copia[str(producto.id)]['producto'] = producto

        for item in carrito_copia.values():
            item['precio'] = float(item['precio'])
            item['subtotal'] = item['precio'] * item['cantidad']
            yield item

    def total(self):
        return sum(float(item['precio']) * item['cantidad'] for item in self.carrito.values())
