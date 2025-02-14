from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROLES = [
        ('director', 'Director'),
        ('subdirector', 'Subdirector'),
        ('jefe_departamento', 'Jefe de Departamento'),
        ('coordinador', 'Coordinador'),
        ('usuario', 'Usuario'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')

    # Evitar conflictos con el modelo base de Django
    groups = models.ManyToManyField("auth.Group", related_name="usuario_groups", blank=True)
    user_permissions = models.ManyToManyField("auth.Permission", related_name="usuario_permissions", blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"


class Ticket(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    usuario_creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tickets_creados')
    usuario_asignado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.estado}"
