from django.urls import path
from . import views
from .views import editar_ticket_view, eliminar_ticket_view, gestionar_tickets_view, gestionar_usuario_view, editar_usuario_view, eliminar_usuario_view

urlpatterns = [
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("crear-ticket/", views.crear_ticket_view, name="crear_ticket"),
    path("generar-reportes/", views.generar_reportes_view, name="generar_reportes"),
    path("filtrar-actividades/", views.filtrar_actividades_view, name="filtrar_actividades"),
    path("ticket/<int:ticket_id>/responder/", views.responder_ticket_view, name="responder_ticket"),
    path("tickets-respondidos/", views.tickets_respondidos_view, name="tickets_respondidos"),
    path("gestionar-usuario/", views.gestionar_usuario_view, name="gestionar_usuario"),
    path("gestionar-tickets/", views.gestionar_tickets_view, name="gestionar_tickets"),
    path('gestionar-usuario/', gestionar_usuario_view, name='gestionar_usuario'),
    path("editar-usuario/", views.editar_usuario_view, name="editar_usuario"),
    path('eliminar-usuario/<int:user_id>/', eliminar_usuario_view, name='eliminar_usuario'),
    path("gestionar-tickets/", gestionar_tickets_view, name="gestionar_tickets"),
    path("editar-ticket/<int:ticket_id>/", editar_ticket_view, name="editar_ticket"),
    path("eliminar-ticket/<int:ticket_id>/", eliminar_ticket_view, name="eliminar_ticket"),

]


