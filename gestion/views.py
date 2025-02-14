from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Usuario, Ticket


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Debe ingresar usuario y contraseña.")
            return render(request, "pages/login.html")

        print(f"Intentando autenticar usuario: {username}")  # Debug en la terminal
        user = authenticate(request, username=username, password=password)

        if user:
            print(f"Usuario autenticado correctamente: {user}")  # Debug en la terminal
            login(request, user)
            return redirect("dashboard")  # Redirige al dashboard según el rol
        else:
            print("Error: Usuario o contraseña incorrectos")  # Debug en la terminal
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "pages/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request):
    user_role = request.user.rol
    if user_role == "coordinador":
        return render(request, "roles/coordinador.html")
    elif user_role == "director":
        return render(request, "roles/director.html")
    elif user_role == "subdirector":
        return render(request, "roles/subdirector.html")
    elif user_role == "jefe_departamento":
        return render(request, "roles/jefe_departamento.html")
    else:
        return render(request, "roles/usuario.html")


@login_required
def crear_ticket_view(request):
    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()

        if not titulo or not descripcion:
            messages.error(request, "Debe ingresar título y descripción del ticket.")
            return render(request, "pages/create_ticket.html")

        ticket = Ticket(
            titulo=titulo,
            descripcion=descripcion,
            usuario_creador=request.user
        )
        ticket.save()
        messages.success(request, "Ticket creado exitosamente.")
        return redirect("dashboard")

    return render(request, "pages/create_ticket.html")


@login_required
def lista_usuarios_view(request):
    usuarios = Usuario.objects.all()
    return render(request, "pages/user_list.html", {"usuarios": usuarios})

@login_required
def generar_reportes_view(request):
    return render(request, "pages/generar_reportes.html")

@login_required
def historial_view(request):
    return render(request, "pages/historial.html")

@login_required
def filtrar_actividades_view(request):
    return render(request, "pages/filtrar_actividades.html")

