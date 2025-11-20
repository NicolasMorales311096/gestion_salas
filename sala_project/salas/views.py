from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import logout, authenticate, login

from .models import Sala, Reserva, RegistroAcceso
from .forms import ReservaForm, EstudianteLoginForm, AdminLoginForm


def home(request):
    """
    Página principal:
    - Lista todas las salas
    - Actualiza su disponibilidad según reservas activas
    - Envía totales para el resumen
    """
    salas = Sala.objects.all().order_by('nombre')

    # Actualizar disponibilidad de cada sala (por si hay reservas activas)
    for sala in salas:
        sala.actualizar_disponibilidad()

    total_salas = salas.count()
    salas_disponibles = salas.filter(disponible=True).count()

    context = {
        'salas': salas,
        'total_salas': total_salas,
        'salas_disponibles': salas_disponibles,
    }
    return render(request, 'salas/home.html', context)


def detalle_sala(request, sala_id):
    """
    Muestra el detalle de una sala y, si existe,
    su reserva actual (con hora_fin en el futuro).
    """
    sala = get_object_or_404(Sala, id=sala_id)

    reserva_actual = (
        Reserva.objects.filter(sala=sala, hora_fin__gt=timezone.now())
        .order_by('-hora_inicio')
        .first()
    )

    context = {
        'sala': sala,
        'reserva': reserva_actual,
    }
    return render(request, 'salas/detalle_sala.html', context)


def reservar_sala(request):
    """
    Crea una nueva reserva usando un ModelForm.
    Registra el movimiento en la bitácora (RegistroAcceso).
    """
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save()  # el modelo ya calcula hora_fin

            # Determinar quién hizo la reserva
            tipo_usuario = 'INVITADO'
            username = None
            rut = reserva.rut
            carrera = None
            detalle = f"Reserva sala: {reserva.sala.nombre}"

            if request.user.is_authenticated and request.user.is_staff:
                tipo_usuario = 'ADMIN'
                username = request.user.username
            elif request.session.get('es_estudiante'):
                tipo_usuario = 'ESTUDIANTE'
                rut = request.session.get('estudiante_rut', rut)
                carrera = request.session.get('estudiante_carrera')

            RegistroAcceso.objects.create(
                tipo_usuario=tipo_usuario,
                accion='RESERVA',
                username=username,
                rut=rut,
                carrera=carrera,
                detalle=detalle
            )

            return redirect('home')
    else:
        form = ReservaForm()

    return render(request, 'salas/reservar_sala.html', {'form': form})


def login_estudiante(request):
    """
    Login simple de estudiante:
    - No crea usuarios de Django
    - Guarda RUT y carrera en la sesión
    - Registra el inicio de sesión en la bitácora
    """
    if request.method == 'POST':
        form = EstudianteLoginForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            carrera = form.cleaned_data['carrera']

            request.session['es_estudiante'] = True
            request.session['estudiante_rut'] = rut
            request.session['estudiante_carrera'] = carrera

            # Registrar login en bitácora
            RegistroAcceso.objects.create(
                tipo_usuario='ESTUDIANTE',
                accion='LOGIN',
                rut=rut,
                carrera=carrera,
                detalle='Inicio de sesión estudiante'
            )

            return redirect('home')
    else:
        form = EstudianteLoginForm()

    return render(request, 'salas/login_estudiante.html', {'form': form})


def login_admin(request):
    """
    Login de administrador usando el usuario de Django (admin/admin123).
    Solo permite acceso a usuarios con is_staff=True.
    También registra el inicio de sesión en la bitácora.
    """
    error = None

    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_staff:
                login(request, user)

                # Registrar login en bitácora
                RegistroAcceso.objects.create(
                    tipo_usuario='ADMIN',
                    accion='LOGIN',
                    username=user.username,
                    detalle='Inicio de sesión administrador'
                )

                return redirect('home')
            else:
                error = "Credenciales inválidas o usuario sin permisos de administrador."
    else:
        form = AdminLoginForm()

    context = {
        'form': form,
        'error': error,
    }
    return render(request, 'salas/login_admin.html', context)


def logout_view(request):
    """
    Cierra cualquier sesión:
    - Si es admin autenticado de Django → registra LOGOUT y hace logout()
    - Si es estudiante en sesión → registra LOGOUT y limpia la sesión
    """
    # Guardar datos antes de limpiar
    es_admin = request.user.is_authenticated and request.user.is_staff
    username = request.user.username if es_admin else None

    es_estudiante = request.session.get('es_estudiante', False)
    rut_est = request.session.get('estudiante_rut')
    carrera_est = request.session.get('estudiante_carrera')

    # Registrar logout admin si aplica
    if es_admin:
        RegistroAcceso.objects.create(
            tipo_usuario='ADMIN',
            accion='LOGOUT',
            username=username,
            detalle='Cierre de sesión administrador'
        )

    # Registrar logout estudiante si aplica
    if es_estudiante:
        RegistroAcceso.objects.create(
            tipo_usuario='ESTUDIANTE',
            accion='LOGOUT',
            rut=rut_est,
            carrera=carrera_est,
            detalle='Cierre de sesión estudiante'
        )

    # Cerrar sesión Django (admin)
    logout(request)

    # Limpiar datos de estudiante
    request.session.pop('es_estudiante', None)
    request.session.pop('estudiante_rut', None)
    request.session.pop('estudiante_carrera', None)

    return redirect('home')
