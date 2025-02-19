from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("crear-ticket/", views.crear_ticket_view, name="crear_ticket"),
    path("generar-reportes/", views.generar_reportes_view, name="generar_reportes"),
    path("filtrar-actividades/", views.filtrar_actividades_view, name="filtrar_actividades"),
    path("ticket/<int:ticket_id>/responder/", views.responder_ticket_view, name="responder_ticket"),
    path("tickets-respondidos/", views.tickets_respondidos_view, name="tickets_respondidos"),

]


