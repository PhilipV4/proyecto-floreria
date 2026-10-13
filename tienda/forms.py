from django import forms
from django.core.exceptions import ValidationError
from .models import *


#registro usuario

User = get_user_model()

class RegistroForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@correo.cl'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este correo electrónico.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
######

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'precio', 'descripcion', 'stock', 
            'categoria', 'ocasion', 
            'imagen', 'disponible'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ocasion': forms.Select(attrs={'class': 'form-select'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'precio': 'Precio',
            'descripcion': 'Descripción', 
            'stock': 'Stock',
            'categoria': 'Categoría',
            'ocasion': 'Ocasión',
            'disponible': 'Disponible',
            'imagen': 'Imagen del Producto',
        }
    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise ValidationError("El precio debe ser un número positivo mayor que cero.")
        return precio

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class OcasionForm(forms.ModelForm):
    class Meta:
        model = Ocasion
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

User = get_user_model()

# Listado oficial de comunas de la Región Metropolitana
COMUNAS_RM_CHOICES = [
    ('', 'Selecciona tu comuna'),
    # Provincia de Santiago
    ('Santiago', 'Santiago'),
    ('Cerrillos', 'Cerrillos'),
    ('Cerro Navia', 'Cerro Navia'),
    ('Conchalí', 'Conchalí'),
    ('El Bosque', 'El Bosque'),
    ('Estación Central', 'Estación Central'),
    ('Huechuraba', 'Huechuraba'),
    ('Independencia', 'Independencia'),
    ('La Cisterna', 'La Cisterna'),
    ('La Florida', 'La Florida'),
    ('La Granja', 'La Granja'),
    ('La Pintana', 'La Pintana'),
    ('La Reina', 'La Reina'),
    ('Las Condes', 'Las Condes'),
    ('Lo Barnechea', 'Lo Barnechea'),
    ('Lo Espejo', 'Lo Espejo'),
    ('Lo Prado', 'Lo Prado'),
    ('Macul', 'Macul'),
    ('Maipú', 'Maipú'),
    ('Ñuñoa', 'Ñuñoa'),
    ('Pedro Aguirre Cerda', 'Pedro Aguirre Cerda'),
    ('Peñalolén', 'Peñalolén'),
    ('Providencia', 'Providencia'),
    ('Pudahuel', 'Pudahuel'),
    ('Quilicura', 'Quilicura'),
    ('Quinta Normal', 'Quinta Normal'),
    ('Recoleta', 'Recoleta'),
    ('Renca', 'Renca'),
    ('San Joaquín', 'San Joaquín'),
    ('San Miguel', 'San Miguel'),
    ('San Ramón', 'San Ramón'),
    ('Vitacura', 'Vitacura'),
    
    # Provincia de Talagante
    ('Padre Hurtado', 'Padre Hurtado'),
    ('Talagante', 'Talagante'),
    ('El Monte', 'El Monte'),
    ('Isla de Maipo', 'Isla de Maipo'),
    ('Peñaflor', 'Peñaflor'),
    
    # Provincia de Maipo
    ('San Bernardo', 'San Bernardo'),
    ('Buin', 'Buin'),
    ('Paine', 'Paine'),
    ('Calera de Tango', 'Calera de Tango'),
    
    # Provincia de Cordillera
    ('Puente Alto', 'Puente Alto'),
    ('Pirque', 'Pirque'),
    ('San José de Maipo', 'San José de Maipo'),
    
    # Provincia de Chacabuco
    ('Colina', 'Colina'),
    ('Lampa', 'Lampa'),
    ('Tiltil', 'Tiltil'),
]

class EditarPerfilForm(forms.ModelForm):
    # Campos opcionales vinculados al modelo base User (Nombre y Apellido)
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'})
    )

    # Selector estricto de comuna limitado a la RM
    comuna = forms.ChoiceField(
        choices=COMUNAS_RM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Comuna"
    )

    class Meta:
        model = UserProfile
        fields = ['telefono', 'direccion', 'comuna']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+569XXXXXXXX'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Av. Principal 123'}),
        }