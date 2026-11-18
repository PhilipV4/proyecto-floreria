
from django.contrib import admin
from .models import  Orden, ItemOrden, TarifaComuna

class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0  # No muestra filas vacías adicionales por defecto
    readonly_fields = ('producto_nombre', 'precio_unitario', 'cantidad', 'subtotal')
    can_delete = False


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombre_destinatario', 'comuna', 'fecha_entrega', 'total', 'pagado', 'fecha_creacion')
    list_filter = ('pagado', 'estado_envio', 'fecha_entrega')
    search_fields = ('nombre_destinatario', 'direccion_envio', 'comuna', 'usuario__username', 'usuario__email')
    readonly_fields = ('fecha_creacion', 'total', 'token_ws', 'codigo_autorizacion')
    inlines = [ItemOrdenInline] # Muestra los ítems de la orden dentro de la misma vista



@admin.register(TarifaComuna)
class TarifaComunaAdmin(admin.ModelAdmin):
    list_display = ('comuna', 'precio_envio')
    search_fields = ('comuna',)