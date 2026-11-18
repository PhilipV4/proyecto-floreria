from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

@receiver(user_logged_in)
def restaurar_carrito_en_login(sender, request, user, **kwargs):
    """
    Se ejecuta automáticamente justo después de que un usuario hace login exitoso.
    restaura su carrito guardado y lo fusiona si traía productos como invitado.
    """
    if user.carrito_guardado:
        # Obtenemos el carrito actual de la sesión (lo que traía como invitado)
        carrito_sesion = request.session.get('session_key', {})
        
        if carrito_sesion:
            # Si el usuario ya tenía productos en la sesión antes de loguearse,
            # fusionamos ambos diccionarios sumando las cantidades
            for producto_id, cantidad in user.carrito_guardado.items():
                if producto_id in carrito_sesion:
                    carrito_sesion[producto_id] += cantidad
                else:
                    carrito_sesion[producto_id] = cantidad
        else:
            # Si la sesión de invitado estaba vacía, cargamos directamente lo que tenía guardado
            carrito_sesion = user.carrito_guardado
            
        # Asignamos el carrito definitivo a la sesión y guardamos
        request.session['session_key'] = carrito_sesion
        request.session.modified = True