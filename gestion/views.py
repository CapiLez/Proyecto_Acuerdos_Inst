from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Usuario, Ticket
from collections import defaultdict


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Debe ingresar usuario y contraseña.")
            return render(request, "pages/login.html")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")  # Redirige al dashboard según el rol
        else:
            messages.error(request, "Credenciales incorrectas.")
            return render(request, "pages/login.html")

    return render(request, "pages/login.html")

@login_required
def dashboard_view(request):
    if request.user.rol == "director":
        return render(request, "roles/director.html")
    elif request.user.rol == "subdirector":
        return render(request, "roles/subdirector.html")
    elif request.user.rol == "jefe_departamento":
        return render(request, "roles/jefe_departamento.html")
    elif request.user.rol == "coordinador":
        return render(request, "roles/coordinador.html")
    else:
        return render(request, "roles/usuario.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def crear_ticket_view(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        asignado_a_id = request.POST.get("asignado_a")
        estado = request.POST.get("estado")
        usuario_asignado = Usuario.objects.get(id=asignado_a_id)
        usuario_creador = request.user
        
        Ticket.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            usuario_asignado=usuario_asignado,
            usuario_creador=usuario_creador,
            estado=estado
        )
        messages.success(request, "Ticket creado exitosamente.")
        return render(request, "pages/create_ticket.html", {"usuarios": Usuario.objects.all()})

    usuarios = Usuario.objects.all()
    return render(request, "pages/create_ticket.html", {"usuarios": usuarios})


@login_required
def lista_usuarios_view(request):
    usuarios = Usuario.objects.all()
    return render(request, "pages/user_list.html", {"usuarios": usuarios})

@login_required
def generar_reportes_view(request):
    reportes = {}
    search_query = request.GET.get("search", "").strip()
    
    if search_query:
        usuarios = Usuario.objects.filter(Q(username__icontains=search_query))
    else:
        usuarios = Usuario.objects.all()
    
    for usuario in usuarios:
        tickets = Ticket.objects.filter(usuario_asignado=usuario)
        reportes[usuario.username] = list(tickets)
    
    return render(request, "pages/gen_reporte.html", {"reportes": reportes, "search_query": search_query})

@login_required
def historial_view(request):
    tickets = Ticket.objects.all().order_by("-fecha_creacion")
    return render(request, "pages/historial.html", {"tickets": tickets})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Usuario, Ticket
from collections import defaultdict


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Debe ingresar usuario y contraseña.")
            return render(request, "pages/login.html")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")  # Redirige al dashboard según el rol
        else:
            messages.error(request, "Credenciales incorrectas.")
            return render(request, "pages/login.html")

    return render(request, "pages/login.html")

@login_required
def filtrar_actividades_view(request):
    tickets = Ticket.objects.all()
    usuarios = Usuario.objects.all()
    
    usuario_asignado = request.GET.get("usuario_asignado", "")
    usuario_creador = request.GET.get("usuario_creador", "")
    estado = request.GET.get("estado", "")
    prioridad = request.GET.get("prioridad", "")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")
    
    if usuario_asignado:
        tickets = tickets.filter(usuario_asignado_id=usuario_asignado)
    if usuario_creador:
        tickets = tickets.filter(usuario_creador_id=usuario_creador)
    if estado:
        tickets = tickets.filter(estado=estado)
    if prioridad:
        tickets = tickets.filter(prioridad=prioridad)
    if fecha_inicio and fecha_fin:
        tickets = tickets.filter(fecha_creacion__range=[fecha_inicio, fecha_fin])
    
    return render(request, "pages/filtrar_actividades.html", {"tickets": tickets, "usuarios": usuarios})

