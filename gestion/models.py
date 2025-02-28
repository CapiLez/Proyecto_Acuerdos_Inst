from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROLES = [
        ('administrador', 'Administrador'),
        ('director', 'Director'),
        ('subdirector', 'Subdirector'),
        ('jefe_departamento', 'Jefe de Departamento'),
        ('coordinador', 'Coordinador'),
        ('usuario', 'Usuario'),
    ]

    DIRECCIONES = [
        ('coordinacion_general', 'Coordinación General'),
        ('secretaria_tecnica', 'Secretaria Técnica y Seguimiento Institucional'),
        ('admin_finanzas', 'Unidad de Administración y Finanzas'),
        ('juridico', 'Unidad de Apoyo Jurídico'),
        ('control_interno', 'Órgano Interno de Control'),
        ('transparencia', 'Unidad de Transparencia'),
        ('informatica', 'Unidad de Apoyo Técnico e Informático'),
        ('voluntariado', 'Dirección de Voluntariado y Vinculación Institucional con Sociedad Civil'),
        ('alimentarios', 'Dirección de Servicios Alimentarios y Desarrollo Comunitario'),
        ('orientacion_familiar', 'Dirección de Orientación Familiar y Asistencia Social'),
        ('rehabilitacion', 'Dirección de Rehabilitación e Inclusión'),
        ('centros_asistenciales', 'Dirección de Centros Asistenciales'),
        ('proteccion_nna', 'Secretaria Ejecutiva del Sistema Estatal de Protección de los Derechos de Niñas, Niños y Adolescentes'),
        ('procuraduria_familia', 'Procuraduría Estatal de Protección de la Familia y de los Derechos de las Niñas, Niños y Adolescentes'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    direccion = models.CharField(max_length=50, choices=DIRECCIONES, default='coordinacion_general')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()}) - {self.get_direccion_display()}"

class Ticket(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    usuario_creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tickets_creados')
    usuario_asignado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.estado}" 


class Respuesta(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='respuestas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta de {self.usuario.username} en {self.ticket.titulo}"

