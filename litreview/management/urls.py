from django.urls import path

from .views import CreateTicketView, DeleteTicketView, EditTicketView, index

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
    path(
        "ticket/delete/<int:pk>/",
        DeleteTicketView.as_view(),
        name="ticket_delete",
    ),
]
