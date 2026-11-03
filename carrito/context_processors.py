from .carrito import Carrito

#crear concext processor para que el carrito este disponible en todas las paginas

def carrito(request):
    #devolver los datos default del carrito
    return {'carrito': Carrito(request)}