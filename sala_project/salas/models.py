from django.db import models
from django.utils import timezone
from datetime import timedelta


class Sala(models.Model):
    nombre = models.CharField(max_length=100)
    capacidad_maxima = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    def actualizar_disponibilidad(self):
        # Verifica si hay reservas con hora_fin en el futuro
        reserva_activa = self.reserva_set.filter(hora_fin__gt=timezone.now()).exists()
        self.disponible = not reserva_activa
        self.save()


class Reserva(models.Model):
    rut = models.CharField(max_length=12)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    hora_inicio = models.DateTimeField(auto_now_add=True)
    hora_fin = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Si es nueva reserva, hora_fin = hora_inicio + 2 horas
        if not self.pk:
            inicio = self.hora_inicio or timezone.now()
            self.hora_fin = inicio + timedelta(hours=2)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.rut} - {self.sala.nombre}"


class RegistroAcceso(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('ESTUDIANTE', 'Estudiante'),
        ('INVITADO', 'Invitado'),
    ]

    ACCION_CHOICES = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('RESERVA', 'Reserva creada'),
    ]

    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)

    username = models.CharField(
        max_length=150, blank=True, null=True,
        help_text="Nombre de usuario (en el caso del administrador)"
    )
    rut = models.CharField(
        max_length=12, blank=True, null=True,
        help_text="RUT del estudiante si aplica"
    )
    carrera = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Carrera del estudiante si aplica"
    )

    detalle = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Detalle adicional (ej: sala reservada, etc.)"
    )

    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fecha_hora:%Y-%m-%d %H:%M} - {self.tipo_usuario} - {self.accion}"
