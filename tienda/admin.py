from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'role', 'telefono', 'comuna', 'is_staff')
    
    # Agregamos secciones personalizadas al editar un usuario en el admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Envío y Rol (Florería)', {'fields': ('role', 'telefono', 'direccion', 'comuna')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Envío y Rol (Florería)', {'fields': ('email', 'role', 'telefono', 'direccion', 'comuna')}),
    )