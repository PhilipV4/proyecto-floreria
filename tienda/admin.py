from django.contrib import admin

from tienda.models import *

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Ocasion)
class OcasionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'ocasion', 'disponible', 'creado_el', 'actualizado_el')
    list_filter = ('categoria', 'ocasion', 'disponible')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio', 'stock', 'disponible')
    ordering = ('-creado_el',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'direccion', 'ciudad', 'region', 'pais', 'codigo_postal')
    search_fields = ('user__username', 'user__email', 'direccion', 'ciudad', 'region', 'pais', 'codigo_postal')
    list_filter = ('role',)
    ordering = ('user__username',)