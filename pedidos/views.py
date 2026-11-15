
# Create your views here.
from django.shortcuts import render, redirect
from .forms import CheckoutForm
from .models import ItemOrden , Orden, TarifaComuna
from carrito.carrito import Carrito

import json

from .utils import enviar_correo_orden_exitosa

def iniciar_checkout(request):
    carrito = Carrito(request)
    
    if len(carrito) == 0:
        return redirect('carrito_detalle')

    tiene_perfil = request.user.is_authenticated and bool(getattr(request.user, 'direccion', None))
    
    # Por defecto seleccionamos 'registrada' si tiene perfil, de lo contrario 'otra'
    tipo_envio = 'registrada' if tiene_perfil else 'otra'

    if request.method == 'POST':
        tipo_envio = request.POST.get('tipo_envio', 'registrada')
        form = CheckoutForm(request.POST)
        
        if request.user.is_authenticated:
            form.data = form.data.copy()
            form.data['email_cliente'] = request.user.email
            
            if tipo_envio == 'registrada':
                form.data['direccion_envio'] = getattr(request.user, 'direccion', '')
                form.data['comuna'] = getattr(request.user, 'comuna', '')
                form.data['telefono_destinatario'] = getattr(request.user, 'telefono', '')
                if not form.data.get('nombre_destinatario'):
                    form.data['nombre_destinatario'] = request.user.get_full_name() or request.user.username

        if form.is_valid():
            orden = form.save(commit=False)
            
            if request.user.is_authenticated:
                orden.usuario = request.user

            comuna_elegida = form.cleaned_data.get('comuna')
            #costo tarifa de envio
            try:
                tarifa = TarifaComuna.objects.get(comuna=comuna_elegida)
                orden.costo_envio = tarifa.precio_envio
            except TarifaComuna.DoesNotExist:
                orden.costo_envio = 0  # Si no se encuentra la comuna, el costo de envío será 0


            #calcular total general dek carrito + envio
            orden.total = carrito.total() + orden.costo_envio
            orden.save()
            
            for item in carrito:
                ItemOrden.objects.create(
                    orden=orden,
                    producto_nombre=item['producto'].nombre,
                    precio_unitario=item['precio'],
                    cantidad=item['cantidad']
                )

            enviar_correo_orden_exitosa(orden)

            # Limpiar el carrito y la sesión después de guardar la orden
            request.session['session_key'] = {}
            request.session.modified = True
            if request.user.is_authenticated:
                request.user.carrito_guardado = {}
                request.user.save(update_fields=['carrito_guardado'])
            
            request.session['orden_id'] = orden.id
            return redirect('pago_exitoso')
    else:
        form = CheckoutForm()

    tarifas_qs = TarifaComuna.objects.all()
    tarifas_dict = {t.comuna: float(t.precio_envio) for t in tarifas_qs}

    context = {
        'form': form,
        'carrito': carrito,
        'tiene_perfil': tiene_perfil,
        'tipo_envio_seleccionado': tipo_envio, 
        'tarifas_json': json.dumps(tarifas_dict),  # <--- Pasamos las tarifas en JSON
        'comuna_usuario': getattr(request.user, 'comuna', '') if request.user.is_authenticated else '',
    }
    return render(request, 'pedidos/checkout.html', context)

def pago_exitoso(request):
    orden_id = request.session.get('orden_id')
    orden = None
    if orden_id:
        try:
            orden = Orden.objects.get(id=orden_id)
        except Orden.DoesNotExist:
            pass

    context = {
        'orden': orden,
    }
    return render(request, 'pedidos/exito.html', context)


def previsualizar_correo(request, orden_id):
    """
    Vista temporal para renderizar el correo en el navegador web
    y ver cómo queda el diseño HTML.
    URL de prueba: http://127.0.0.1:8000/pedidos/preview-email/1/
    """
    # Buscamos una orden existente (por ejemplo, la orden ID 1)
    orden = Orden.objects.get(id=orden_id)
    
    # Renderizamos directamente la plantilla del correo pasando la orden
    return render(request, 'pedidos/email_confirmacion.html', {'orden': orden})