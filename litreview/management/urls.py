from django.urls import path

from .views import (
    CreateReviewView,
    CreateTicketAndReviewView,
    CreateTicketView,
    DeleteReviewView,
    DeleteTicketView,
    EditReviewView,
    EditTicketView,
    ReviewList,
    index,
)

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
    path(
        "review/create/<int:pk>",
        CreateReviewView.as_view(),
        name="review_create",
    ),
    path("reviews/list/", ReviewList, name="reviews_list"),
    path(
        "review/edit/<int:pk>/",
        EditReviewView.as_view(),
        name="review_edit",
    ),
    path(
        "review/delete/<int:pk>/",
        DeleteReviewView.as_view(),
        name="review_delete",
    ),
    path(
        "ticket_review/create",
        CreateTicketAndReviewView.as_view(),
        name="create_ticket_review",
    ),
]
