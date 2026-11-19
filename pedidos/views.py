
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CheckoutForm
from .models import ItemOrden , Orden, TarifaComuna
from carrito.carrito import Carrito
from .services import WebpayService
from django.urls import reverse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from tienda.decorators import role_required
from django.contrib.auth.decorators import login_required

from .utils import enviar_correo_orden_exitosa

def iniciar_checkout(request):
    carrito = Carrito(request)
    
    if len(carrito) == 0:
        return redirect('carrito_detalle')

    # Verificamos qué datos tiene guardados el usuario
    tiene_direccion = request.user.is_authenticated and bool(getattr(request.user, 'direccion', None)) and bool(getattr(request.user, 'comuna', None))
    
    tipo_envio = 'registrada' if tiene_direccion else 'otra'

    if request.method == 'POST':
        tipo_envio = request.POST.get('tipo_envio', 'registrada')
        form = CheckoutForm(request.POST)
        
        if request.user.is_authenticated:
            form.data = form.data.copy()
            form.data['email_cliente'] = request.user.email
            
            # Si eligió usar su dirección registrada, inyectamos la dirección y comuna del perfil
            if tipo_envio == 'registrada' and tiene_direccion:
                form.data['calle'] = getattr(request.user, 'direccion', '')
                form.data['comuna'] = getattr(request.user, 'comuna', '')
            
            # Si el usuario ya tiene nombre o teléfono en su perfil, los auto-completamos si vinieron vacíos
            if not form.data.get('nombre_destinatario') and getattr(request.user, 'first_name', None):
                form.data['nombre_destinatario'] = request.user.get_full_name()
            if not form.data.get('telefono_destinatario') and getattr(request.user, 'telefono', None):
                form.data['telefono_destinatario'] = request.user.telefono

        if form.is_valid():
            orden = form.save(commit=False)
            
            if request.user.is_authenticated:
                orden.usuario = request.user

            comuna_elegida = form.cleaned_data.get('comuna')
            try:
                tarifa = TarifaComuna.objects.get(comuna=comuna_elegida)
                orden.costo_envio = tarifa.precio_envio
            except TarifaComuna.DoesNotExist:
                orden.costo_envio = 0

            orden.total = carrito.total() + orden.costo_envio
            orden.pagado = False
            orden.save()
            
            for item in carrito:
                ItemOrden.objects.create(
                orden=orden,
                producto_nombre=item['producto'].nombre,
                precio_unitario=item['precio'],
                cantidad=item['cantidad']
    )
            
            request.session['orden_id'] = orden.id
            return redirect('iniciar_pago')
    else:
        # Pre-llenamos el formulario con lo que el usuario tenga en su cuenta
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['email_cliente'] = request.user.email
            if getattr(request.user, 'first_name', None):
                initial_data['nombre_destinatario'] = request.user.get_full_name()
            if getattr(request.user, 'telefono', None):
                initial_data['telefono_destinatario'] = request.user.telefono
        
        form = CheckoutForm(initial=initial_data)

    tarifas_qs = TarifaComuna.objects.all()
    tarifas_dict = {t.comuna: float(t.precio_envio) for t in tarifas_qs}

    context = {
        'form': form,
        'carrito': carrito,
        'tiene_perfil': tiene_direccion,
        'tipo_envio_seleccionado': tipo_envio, 
        'tarifas_json': json.dumps(tarifas_dict),
        'comuna_usuario': getattr(request.user, 'comuna', '') if request.user.is_authenticated else '',
        # Pasamos variables para saber qué le falta exactamente al usuario
        'user_tiene_nombre': bool(getattr(request.user, 'first_name', None)),
        'user_tiene_telefono': bool(getattr(request.user, 'telefono', None)),
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

#WEBPAY

def iniciar_pago(request):
    orden_id = request.session.get('orden_id')
    if not orden_id:
        return redirect('carrito_detalle')

    try:
        orden = Orden.objects.get(id=orden_id, pagado=False)
    except Orden.DoesNotExist:
        return redirect('carrito_detalle')

    buy_order = f"ORD-{orden.id}"
    session_id = request.session.session_key or f"SES-{orden.id}"
    amount = int(orden.total)
    return_url = request.build_absolute_uri(reverse('webpay_retorno'))

    # Llamada limpia al servicio
    response = WebpayService.crear_transaccion(buy_order, session_id, amount, return_url)

    orden.token_ws = response['token']
    orden.save(update_fields=['token_ws'])

    return render(request, 'pedidos/redirigir_webpay.html', {
        'url_webpay': response['url'],
        'token_ws': response['token']
    })

@csrf_exempt
def webpay_retorno(request):
    token_ws = request.GET.get('token_ws') or request.POST.get('token_ws')
    tbk_token = request.GET.get('TBK_TOKEN') or request.POST.get('TBK_TOKEN')

    if tbk_token and not token_ws:
        return render(request, 'pedidos/pago_fallido.html', {
            'motivo': 'Has anulado el pago en Webpay. Tu carrito sigue intacto por si deseas intentarlo nuevamente.'
        })

    if not token_ws:
        return redirect('carrito_detalle')

    try:
        orden = Orden.objects.get(token_ws=token_ws)
    except Orden.DoesNotExist:
        return redirect('carrito_detalle')

    if orden.pagado:
        return redirect('pago_exitoso')

    # Confirmación limpia a través del servicio
    response = WebpayService.confirmar_transaccion(token_ws)

    if response.get('status') == 'AUTHORIZED' and response.get('response_code') == 0:
        orden.pagado = True
        orden.codigo_autorizacion = response.get('authorization_code')
        orden.save(update_fields=['pagado', 'codigo_autorizacion'])

        enviar_correo_orden_exitosa(orden)

        request.session['session_key'] = {}
        request.session.modified = True
        if request.user.is_authenticated:
            request.user.carrito_guardado = {}
            request.user.save(update_fields=['carrito_guardado'])

        request.session['orden_id'] = orden.id
        return redirect('pago_exitoso')
    else:
        return render(request, 'pedidos/pago_fallido.html', {
            'motivo': 'El pago fue rechazado por el banco o tarjeta. Por favor, intenta con otro medio de pago.'
        })



#GESTION PEDIDO
@role_required('admin')
def gestion_pedidos(request):
    # Por defecto mostramos solo pedidos pagados (los fallidos/abandonados no estorban)
    ordenes = Orden.objects.filter(pagado=True).prefetch_related('items').order_by('fecha_entrega', '-id')

    # 1. Filtro por estado de envío
    estado_filtro = request.GET.get('estado', '')
    if estado_filtro in ['pendiente', 'en_camino', 'entregado']:
        ordenes = ordenes.filter(estado_envio=estado_filtro)

    # 2. Filtro por fecha de entrega (ej: ?fecha=hoy o ?fecha=2026-11-17)
    fecha_filtro = request.GET.get('fecha', '')
    hoy = timezone.localdate()
    if fecha_filtro == 'hoy':
        ordenes = ordenes.filter(fecha_entrega=hoy)
    elif fecha_filtro:
        ordenes = ordenes.filter(fecha_entrega=fecha_filtro)

    # 3. Buscador rápido por ID, destinatario, comuna o código Webpay
    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        ordenes = ordenes.filter(
            Q(id__icontains=busqueda.replace('#', '')) |
            Q(nombre_destinatario__icontains=busqueda) |
            Q(comuna__icontains=busqueda) |
            Q(codigo_autorizacion__icontains=busqueda)
        )

    # Contadores rápidos para las tarjetas de resumen superior
    total_pendientes = Orden.objects.filter(pagado=True, estado_envio='pendiente').count()
    total_en_camino = Orden.objects.filter(pagado=True, estado_envio='en_camino').count()
    entregas_hoy = Orden.objects.filter(pagado=True, fecha_entrega=hoy).count()

    context = {
        'ordenes': ordenes,
        'estados_envio': Orden.ESTADOS_ENVIO,
        'estado_filtro': estado_filtro,
        'fecha_filtro': fecha_filtro,
        'busqueda': busqueda,
        'total_pendientes': total_pendientes,
        'total_en_camino': total_en_camino,
        'entregas_hoy': entregas_hoy,
        'hoy': hoy,
    }
    return render(request, 'admin/gestion_pedidos.html', context)


@role_required('admin')
def actualizar_estado_envio(request, orden_id):
    if request.method == 'POST':
        orden = get_object_or_404(Orden, id=orden_id, pagado=True)
        nuevo_estado = request.POST.get('estado_envio')
        
        estados_validos = dict(Orden.ESTADOS_ENVIO).keys()
        if nuevo_estado in estados_validos:
            orden.estado_envio = nuevo_estado
            orden.save(update_fields=['estado_envio'])
            messages.success(
            request,
            f"Orden #{orden.id} actualizada a '{orden.get_estado_envio_display()}'.",
            extra_tags='admin_pedidos'
        )
        else:
            messages.error(request, "Estado de envío no válido.")

    # Redirige manteniendo los filtros que el administrador tenía activos
    return redirect(request.META.get('HTTP_REFERER', 'gestion_pedidos'))

@login_required
def mis_pedidos(request):
    ordenes = Orden.objects.filter(
        usuario=request.user, 
        pagado=True
    ).prefetch_related('items').order_by('-fecha_creacion')
    
    return render(request, 'pedidos/mis_pedidos.html', {'ordenes': ordenes})