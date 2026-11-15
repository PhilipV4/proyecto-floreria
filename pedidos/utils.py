from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def enviar_correo_orden_exitosa(orden):
    """
    Envía un correo HTML de confirmación al usuario cuando la orden es creada con éxito.
    """
    if not orden.email_cliente:
        return  # Si no hay usuario o correo asociado, no enviamos nada

    subject = f'🌸 Confirmación de tu Pedido #{orden.id} - ¡Gracias por confiar en nosotros!'
    
    # Renderizamos la plantilla HTML con los datos de la orden
    html_content = render_to_string('pedidos/email_confirmacion.html', {'orden': orden})

    email = EmailMessage(
        subject=subject,
        body=html_content,
        to=[orden.email_cliente],
    )
    email.content_subtype = 'html'  # Indicamos que el cuerpo es HTML
    
    try:
        email.send(fail_silently=False)
    except Exception as e:
        print(f"Error al enviar el correo de confirmación: {e}")