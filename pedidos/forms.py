from django import forms
from .models import Orden
from django.core.validators import RegexValidator
from datetime import date
import re



# Listado oficial de comunas de la Región Metropolitana
COMUNAS_RM = [
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

class CheckoutForm(forms.ModelForm):
    telefono_destinatario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '9 1234 5678',
            'maxlength': '11',
            'inputmode': 'tel',
            'pattern': r'^9\s\d{4}\s\d{4}$',
            'title': 'Ingresa un celular chileno válido (ej: 9 1234 5678)'
        }),
        label='Teléfono de contacto (opcional)'
    )

    # Campos separados para la interfaz (no existen en models.py)
    calle = forms.CharField(
        max_length=180,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Av. Camino a Melipilla 1234',
            'autocomplete': 'street-address'
        }),
        label='Calle y número'
    )

    numero_depto = forms.CharField(
        required=False,  # El depto/casa interior suele ser opcional (si es casa sola con número no hace falta)
        max_length=70,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Depto 502, Torre B, Casa 4',
            'autocomplete': 'address-line2'
        }),
        label='Depto / Torre / Casa interior (opcional)'
    )

    comuna = forms.ChoiceField(
        choices=COMUNAS_RM,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Comuna'
    )

    class Meta:
        model = Orden
        # Quitamos 'direccion_envio' de fields porque la armaremos en clean()
        fields = [
            'email_cliente',
            'nombre_destinatario',
            'telefono_destinatario',
            'comuna',
            'nota_tarjeta',
            'fecha_entrega'
        ]
        widgets = {
            'email_cliente': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.cl'}),
            'nombre_destinatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. María Pérez'}),
            'nota_tarjeta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej. ¡Feliz cumpleaños, te queremos mucho!'}),
            'fecha_entrega': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Selecciona una fecha...'
            }),
        }
        labels = {
            'email_cliente': 'Correo electrónico (para enviarte el comprobante)',
            'nombre_destinatario': 'Nombre de quien recibe',
            'nota_tarjeta': 'Mensaje para la tarjeta (opcional)',
            'fecha_entrega': 'Fecha de entrega',
        }

    def clean_fecha_entrega(self):
        fecha = self.cleaned_data.get('fecha_entrega')
        if fecha and fecha < date.today():
            raise forms.ValidationError("No puedes programar un envío para una fecha en el pasado.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        calle = cleaned_data.get('calle', '').strip()
        numero_depto = cleaned_data.get('numero_depto', '').strip()

        if calle:
            if numero_depto:
                # Resultado: "Av. Providencia 1234, Depto 502, Torre B"
                cleaned_data['direccion_envio'] = f"{calle}, {numero_depto}"
            else:
                cleaned_data['direccion_envio'] = calle

        return cleaned_data

    def save(self, commit=True):
        # Asignamos la dirección combinada a la instancia antes de guardar en BD
        orden = super().save(commit=False)
        orden.direccion_envio = self.cleaned_data.get('direccion_envio', '')
        if commit:
            orden.save()
        return orden