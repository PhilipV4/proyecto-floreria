from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=settings.ROLES)

    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección y número")
    comuna = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        default="", 
        verbose_name="Comuna"
    )
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono de contacto")

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def direccion_completa(self):
        # Como es exclusivo de la RM, fijamos por defecto la Región Metropolitana en el texto final si se desea
        parts = [self.direccion, self.comuna, "Región Metropolitana"]
        return ", ".join(filter(None, parts))
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Ocasion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Ocasión"
        verbose_name_plural = "Ocasiones"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre= models.CharField(max_length=150)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    ocasion = models.ForeignKey(Ocasion, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')

    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-creado_el']

    def __str__(self):
        return self.nombre