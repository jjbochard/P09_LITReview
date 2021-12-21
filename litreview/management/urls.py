from django.urls import path

from .views import CreateTicketView, index

urlpatterns = [
    path("", index, name="index"),
    path(
        "ticket/create/",
        CreateTicketView.as_view(),
        name="ticket_create",
    ),
]
