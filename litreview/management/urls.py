from django.urls import path

from .views import CreateTicketView, EditTicketView, index

urlpatterns = [
    path("", index, name="index"),
    path(
        "ticket/create/",
        CreateTicketView.as_view(),
        name="ticket_create",
    ),
    path(
        "ticket/edit/<int:pk>/",
        EditTicketView.as_view(),
        name="ticket_edit",
    ),
]
