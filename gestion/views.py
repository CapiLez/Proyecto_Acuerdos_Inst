from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Respuesta, Usuario, Ticket


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
    usuario = request.user
    total_tickets = Ticket.objects.filter(usuario_asignado=usuario).count()
    tickets_pendientes = Ticket.objects.filter(usuario_asignado=usuario, estado="pendiente").count()
    tickets_en_proceso = Ticket.objects.filter(usuario_asignado=usuario, estado="en_proceso").count()
    tickets_terminados = Ticket.objects.filter(usuario_asignado=usuario, estado="resuelto").count()

    context = {
        "total_tickets": total_tickets,
        "tickets_pendientes": tickets_pendientes,
        "tickets_en_proceso": tickets_en_proceso,
        "tickets_terminados": tickets_terminados
    }

    return render(request, "dashboard.html", context)


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


@login_required
def responder_ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id, usuario_asignado=request.user)
    if request.method == "POST":
        mensaje = request.POST.get("mensaje")
        nuevo_estado = request.POST.get("estado")
        
        if mensaje:
            Respuesta.objects.create(ticket=ticket, usuario=request.user, mensaje=mensaje)
            messages.success(request, "Respuesta agregada correctamente.")
        
        if nuevo_estado and nuevo_estado in dict(Ticket.ESTADOS):
            ticket.estado = nuevo_estado
            ticket.save()
            messages.success(request, "Estado actualizado correctamente.")
        
        return redirect("responder_ticket", ticket_id=ticket.id)
    
    respuestas = ticket.respuestas.all()
    return render(request, "pages/responder_ticket.html", {"ticket": ticket, "respuestas": respuestas})

@login_required
def filtrar_actividades_view(request):
    if request.user.rol == "coordinador":
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(usuario_asignado=request.user)
    
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
    
    usuarios = Usuario.objects.all()
    return render(request, "pages/filtrar_actividades.html", {"tickets": tickets, "usuarios": usuarios})

