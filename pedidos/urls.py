from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.iniciar_checkout, name='checkout'),
    path('exito/', views.pago_exitoso, name='pago_exitoso'),
    path('preview-email/<int:orden_id>/', views.previsualizar_correo, name='preview_email'),
]