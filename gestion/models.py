from django.contrib.auth.models import AbstractUser, Permission
from django.db import models

# Modelo de Usuario con Roles y Permisos
class Usuario(AbstractUser):
    ROLES = [
        ('director', 'Director'),
        ('subdirector', 'Subdirector'),
        ('jefe_departamento', 'Jefe de Departamento'),
        ('coordinador', 'Coordinador'),
        ('usuario', 'Usuario'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    permisos = models.ManyToManyField(Permission, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
