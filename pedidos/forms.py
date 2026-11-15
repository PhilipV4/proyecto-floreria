from django import forms
from .models import Orden
from django.core.validators import RegexValidator
from datetime import date

validador_telefono_chile = RegexValidator(
    regex=r'^(?:\+?56)?(?:9\d{8}|[2-9]\d{7,8})$',
    message="Ingresa un número de teléfono chileno válido (ej: +56912345678 o 912345678)."
)

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
    # Aplicamos el validador directamente al campo de teléfono
    telefono_destinatario = forms.CharField(
        validators=[validador_telefono_chile],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56912345678'}),
        label='Teléfono de contacto'
    )

    comuna = forms.ChoiceField(
        choices=COMUNAS_RM,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Comuna'
    )

    class Meta:
        model = Orden
        fields = [
            'email_cliente',
            'nombre_destinatario', 
            'telefono_destinatario', 
            'direccion_envio', 
            'comuna', 
            'nota_tarjeta', 
            'fecha_entrega'
        ]
        widgets = {
            'email_cliente': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.cl'}),
            'nombre_destinatario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. María Pérez'}),
            'direccion_envio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Av. Providencia 1234'}),
            'nota_tarjeta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej. ¡Feliz cumpleaños, te queremos mucho!'}),
            'fecha_entrega': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Selecciona una fecha...'
            }),
        }
        labels = {
            'email_cliente': 'Correo electrónico (para enviarte el comprobante)',
            'nombre_destinatario': 'Nombre de quien recibe',
            'direccion_envio': 'Dirección de despacho',
            'nota_tarjeta': 'Mensaje para la tarjeta (opcional)',
            'fecha_entrega': 'Fecha de entrega',
        }

    def clean_fecha_entrega(self):
        fecha = self.cleaned_data.get('fecha_entrega')
        if fecha and fecha < date.today():
            raise forms.ValidationError("No puedes programar un envío para una fecha en el pasado.")
        return fecha

    def clean_telefono_destinatario(self):
        telefono = self.cleaned_data.get('telefono_destinatario', '').strip()
        # Elimina espacios o guiones accidentales ingresados por el usuario
        telefono_limpio = telefono.replace(' ', '').replace('-', '')
        
        # Si el usuario ingresó 9 dígitos empezando por 9, le anteponemos el prefijo +56
        if len(telefono_limpio) == 9 and telefono_limpio.startswith('9'):
            telefono_limpio = f'+56{telefono_limpio}'
            
        return telefono_limpio