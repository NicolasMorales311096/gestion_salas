from django import forms
from .models import Reserva, Sala


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['rut', 'sala']
        labels = {
            'rut': 'RUT de quien reserva',
            'sala': 'Sala a reservar',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar salas disponibles en el formulario
        self.fields['sala'].queryset = Sala.objects.filter(disponible=True)


class EstudianteLoginForm(forms.Form):
    rut = forms.CharField(
        label='RUT',
        max_length=12,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: 12.345.678-9'})
    )
    carrera = forms.CharField(
        label='Carrera',
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: Analista Programador'})
    )


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario administrador',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'admin'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'admin123'})
    )
