from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Respuesta, Usuario, Ticket
from django.contrib import messages
from django.contrib.auth.hashers import make_password


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
    usuario_actual = request.user
    
    # Filtrar tickets asignados al usuario actual
    total_tickets = Ticket.objects.filter(usuario_asignado=usuario_actual).count()
    tickets_pendientes = Ticket.objects.filter(usuario_asignado=usuario_actual, estado="pendiente").count()
    tickets_en_proceso = Ticket.objects.filter(usuario_asignado=usuario_actual, estado="en_progreso").count()
    tickets_completados = Ticket.objects.filter(usuario_asignado=usuario_actual, estado="completado").count()  # <-- Asegurar esta línea

    context = {
        "total_tickets": total_tickets,
        "tickets_pendientes": tickets_pendientes,
        "tickets_en_proceso": tickets_en_proceso,
        "tickets_completados": tickets_completados,  # <-- Asegurar que esta variable existe
    }

    return render(request, "dashboard.html", context)



@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def crear_ticket_view(request):
    usuarios = Usuario.objects.all()

    if request.method == "POST":
        titulo = request.POST.get("titulo")
        descripcion = request.POST.get("descripcion")
        asignado_a_id = request.POST.get("asignado_a")
        prioridad = request.POST.get("prioridad")
        estado = request.POST.get("estado")
        
        if not (titulo and descripcion and asignado_a_id and prioridad and estado):
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            usuario_asignado = get_object_or_404(Usuario, id=asignado_a_id)
            ticket = Ticket.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                usuario_asignado=usuario_asignado,
                usuario_creador=request.user,
                prioridad=prioridad,
                estado=estado
            )
            messages.success(request, f"El ticket '{ticket.titulo}' se creó exitosamente.")

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
    respuestas = ticket.respuestas.all()

    if request.method == "POST":
        mensaje = request.POST.get("mensaje")
        nuevo_estado = request.POST.get("estado")
        
        if not mensaje:
            messages.error(request, "Debe ingresar un mensaje para responder.")
        else:
            Respuesta.objects.create(ticket=ticket, usuario=request.user, mensaje=mensaje)
            messages.success(request, "Respuesta agregada correctamente.")

        if nuevo_estado and nuevo_estado in dict(Ticket.ESTADOS):
            ticket.estado = nuevo_estado
            ticket.save()
            messages.success(request, "Estado del ticket actualizado.")

    return render(request, "pages/responder_ticket.html", {"ticket": ticket, "respuestas": respuestas})


from django.utils import timezone
from datetime import datetime

@login_required
def filtrar_actividades_view(request):
    usuario_actual = request.user

    # Solo el Administrador y el Coordinador pueden ver todas las actividades
    if usuario_actual.rol in ["administrador", "coordinador"]:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(usuario_asignado=usuario_actual)

    # Obtener filtros de la solicitud GET
    usuario_asignado = request.GET.get("usuario_asignado", "")
    usuario_creador = request.GET.get("usuario_creador", "")
    estado = request.GET.get("estado", "")
    prioridad = request.GET.get("prioridad", "")
    fecha_inicio = request.GET.get("fecha_inicio", "")
    fecha_fin = request.GET.get("fecha_fin", "")

    # Aplicar filtros
    if usuario_asignado:
        tickets = tickets.filter(usuario_asignado_id=usuario_asignado)
    if usuario_creador:
        tickets = tickets.filter(usuario_creador_id=usuario_creador)
    if estado:
        tickets = tickets.filter(estado=estado)
    if prioridad:
        tickets = tickets.filter(prioridad=prioridad)
    
    # Convertir fechas a formato con zona horaria
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = timezone.make_aware(datetime.strptime(fecha_inicio, "%Y-%m-%d"))
            fecha_fin = timezone.make_aware(datetime.strptime(fecha_fin, "%Y-%m-%d"))
            tickets = tickets.filter(fecha_creacion__range=[fecha_inicio, fecha_fin])
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")

    usuarios = Usuario.objects.all()
    
    return render(request, "pages/filtrar_actividades.html", {"tickets": tickets, "usuarios": usuarios})



@login_required
def tickets_respondidos_view(request):
    tickets_respondidos = Ticket.objects.filter(respuestas__isnull=False).distinct()
    context = {
        "tickets_respondidos": tickets_respondidos,
    }
    return render(request, "pages/tickets_respondidos.html", context)

@login_required
def gestionar_usuario_view(request):
    usuarios = Usuario.objects.all()

    if request.method == "POST":
        nombre_usuario = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        contraseña = request.POST.get("password")
        rol = request.POST.get("rol")

        if not nombre_usuario or not email or not contraseña or not rol:
            messages.error(request, "Todos los campos son obligatorios.")
        else:
            # Verificar si el usuario ya existe
            if Usuario.objects.filter(username=nombre_usuario).exists():
                messages.error(request, "El usuario ya existe.")
            else:
                # Crear usuario
                usuario = Usuario.objects.create(
                    username=nombre_usuario,
                    email=email,
                    password=make_password(contraseña),  # Encriptar contraseña
                    rol=rol
                )
                messages.success(request, f"Usuario {usuario.username} creado con éxito.")
                return redirect("gestionar_usuario")  # Recargar la página

    return render(request, "pages/gestionar_usuario.html", {"usuarios": usuarios})


@login_required
def gestionar_tickets_view(request):
    tickets = Ticket.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "actualizar":
            ticket_id = request.POST.get("ticket_id")
            nuevo_estado = request.POST.get("estado")

            ticket = get_object_or_404(Ticket, id=ticket_id)
            ticket.estado = nuevo_estado
            ticket.save()
            messages.success(request, f"El ticket '{ticket.titulo}' fue actualizado a '{nuevo_estado}'.")

        elif action == "eliminar":
            ticket_id = request.POST.get("ticket_id")
            ticket = get_object_or_404(Ticket, id=ticket_id)
            ticket.delete()
            messages.success(request, "El ticket fue eliminado correctamente.")

    return render(request, "pages/gestionar_tickets.html", {"tickets": tickets})

@login_required
def editar_usuario_view(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        email = request.POST.get("email")
        password = request.POST.get("password")
        rol = request.POST.get("rol")

        usuario = get_object_or_404(Usuario, id=user_id)

        if email:
            usuario.email = email
        if password:
            usuario.set_password(password)
        if rol:
            usuario.rol = rol

        usuario.save()
        messages.success(request, f"El usuario {usuario.username} ha sido actualizado correctamente.")

    return redirect("gestionar_usuario")

@login_required
def eliminar_usuario_view(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)

    # Evitar que el usuario se elimine a sí mismo
    if request.user == usuario:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("gestionar_usuario")

    usuario.delete()
    messages.success(request, f"El usuario {usuario.username} ha sido eliminado correctamente.")

    return redirect("gestionar_usuario")

@login_required
def editar_ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket.titulo = request.POST.get("titulo", ticket.titulo)
        ticket.estado = request.POST.get("estado", ticket.estado)
        ticket.usuario_asignado_id = request.POST.get("usuario_asignado", ticket.usuario_asignado_id)
        ticket.prioridad = request.POST.get("prioridad", ticket.prioridad)
        ticket.descripcion = request.POST.get("descripcion", ticket.descripcion)  # ✅ Permitir edición del comentario
        ticket.save()

        messages.success(request, f"El ticket '{ticket.titulo}' ha sido actualizado correctamente.")
        return redirect("gestionar_tickets")

    usuarios = Usuario.objects.all()
    return render(request, "pages/editar_ticket.html", {"ticket": ticket, "usuarios": usuarios})


@login_required
def eliminar_ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == "POST":
        ticket.delete()
        messages.success(request, "El ticket ha sido eliminado correctamente.")  # Mensaje de éxito
        return redirect("gestionar_tickets")  # Redirige a la página de gestión de tickets

    return render(request, "pages/eliminar_ticket.html", {"ticket": ticket})
