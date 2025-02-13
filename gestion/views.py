from django.shortcuts import render

from django.shortcuts import render
from .models import Usuario

def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})
