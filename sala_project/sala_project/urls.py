from django.contrib import admin
from django.urls import path
from salas import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('sala/<int:sala_id>/', views.detalle_sala, name='detalle_sala'),
    path('reservar/', views.reservar_sala, name='reservar_sala'),

    # Login estudiante
    path('login-estudiante/', views.login_estudiante, name='login_estudiante'),

    # Login administrador
    path('login-admin/', views.login_admin, name='login_admin'),

    # Logout general
    path('logout/', views.logout_view, name='logout'),
]
