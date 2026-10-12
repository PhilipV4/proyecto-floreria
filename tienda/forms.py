from django import forms
from django.core.exceptions import ValidationError
from .models import *

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