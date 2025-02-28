from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Respuesta, Usuario, Ticket
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import datetime


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
    total_tickets = Ticket.objects.all().count()
    tickets_pendientes = Ticket.objects.filter(estado__iexact="pendiente").count()
    # Permite "en_proceso" o "en proceso"
    tickets_en_proceso = Ticket.objects.filter(Q(estado__iexact="en_proceso") | Q(estado__iexact="en proceso")).count()
    tickets_completados = Ticket.objects.filter(estado__iexact="completado").count()

    direcciones_tickets = []
    for direccion_key, direccion_nombre in Usuario.DIRECCIONES:
        cantidad = Ticket.objects.filter(usuario_asignado__direccion=direccion_key).count()
        direcciones_tickets.append({
            'key': direccion_key,
            'nombre': direccion_nombre,
            'cantidad': cantidad
        })

    context = {
        "total_tickets": total_tickets,
        "tickets_pendientes": tickets_pendientes,
        "tickets_en_proceso": tickets_en_proceso,
        "tickets_completados": tickets_completados,
        "direcciones_tickets": direcciones_tickets,
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

@login_required
def filtrar_actividades_view(request):
    usuario_actual = request.user

    # Filtrar tickets según el usuario o el rol de administrador
    if usuario_actual.rol == "administrador":
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(usuario_asignado=usuario_actual)

    usuario_asignado = request.GET.get("usuario_asignado", "")
    direccion = request.GET.get("direccion", "")
    estado = request.GET.get("estado", "")
    prioridad = request.GET.get("prioridad", "")

    if usuario_asignado:
        tickets = tickets.filter(usuario_asignado_id=usuario_asignado)
    if direccion:
        tickets = tickets.filter(usuario_asignado__direccion=direccion)
    if estado:
        tickets = tickets.filter(estado=estado)
    if prioridad:
        tickets = tickets.filter(prioridad=prioridad)

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
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        rol = request.POST.get("rol")
        direccion = request.POST.get("direccion")

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
        else:
            usuario = Usuario.objects.create(username=username, email=email, rol=rol, direccion=direccion)
            usuario.set_password(password)  # Encriptar la contraseña
            usuario.save()
            messages.success(request, "Usuario creado correctamente.")

    usuarios = Usuario.objects.all()

    # Enviar los roles y direcciones al template
    context = {
        "usuarios": usuarios,
        "roles": Usuario.ROLES,
        "direcciones": Usuario.DIRECCIONES
    }
    
    return render(request, "pages/gestionar_usuario.html", context)

@login_required
def editar_usuario_view(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        rol = request.POST.get("rol")
        direccion = request.POST.get("direccion")

        usuario = get_object_or_404(Usuario, id=user_id)

        cambios_realizados = False
        if email and usuario.email != email:
            usuario.email = email
            cambios_realizados = True
        if password:
            usuario.set_password(password)
            cambios_realizados = True
        if rol and usuario.rol != rol:
            usuario.rol = rol
            cambios_realizados = True
        if direccion and usuario.direccion != direccion:
            usuario.direccion = direccion
            cambios_realizados = True

        if cambios_realizados:
            usuario.save()
            messages.success(request, f"El usuario {usuario.username} ha sido actualizado correctamente.")
        else:
            messages.info(request, "No se realizaron cambios.")

    return redirect("gestionar_usuario")

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

@login_required
def obtener_tickets_por_direccion_view(request):
    direccion = request.GET.get('direccion')

    if not direccion:
        return JsonResponse({"error": "Debe proporcionar una dirección válida"}, status=400)

    data = {
        "pendiente": Ticket.objects.filter(usuario_asignado__direccion=direccion, estado__iexact="pendiente").count(),
        "en_proceso": Ticket.objects.filter(
            usuario_asignado__direccion=direccion
        ).filter(
            Q(estado__iexact="en_proceso") | Q(estado__iexact="en proceso")
        ).count(),
        "completado": Ticket.objects.filter(usuario_asignado__direccion=direccion, estado__iexact="completado").count(),
    }

    return JsonResponse(data)

@login_required
def obtener_tickets_global(request):
    tickets_pendientes = Ticket.objects.filter(estado="pendiente").count()
    tickets_en_proceso = Ticket.objects.filter(estado="en_proceso").count()
    tickets_completados = Ticket.objects.filter(estado="completado").count()

    data = {
        "pendiente": tickets_pendientes,
        "en_proceso": tickets_en_proceso,
        "completado": tickets_completados,
    }
    return JsonResponse(data)

@login_required
def autocompletar_direcciones(request):
    if 'term' in request.GET:
        term = request.GET.get('term', '').lower()
        direcciones = [nombre for _, nombre in Usuario.DIRECCIONES if term in nombre.lower()]
        return JsonResponse(direcciones, safe=False)  # Devuelve la lista en formato JSON
    return JsonResponse([], safe=False)

@login_required
def autocompletar_usuarios(request):
    if 'term' in request.GET:
        term = request.GET.get('term', '').lower()
        usuarios = Usuario.objects.filter(username__icontains=term)[:10]  # Limitar a 10 resultados
        usuarios_nombres = list(usuarios.values_list('username', flat=True))
        return JsonResponse(usuarios_nombres, safe=False)
    return JsonResponse([], safe=False)