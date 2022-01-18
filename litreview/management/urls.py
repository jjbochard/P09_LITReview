from django.urls import path

from .views import (
    FeedView,
    UserPostsView,
    CreateUserFollowsView,
    CreateReviewView,
    CreateTicketAndReviewView,
    CreateTicketView,
    DeleteReviewView,
    DeleteTicketView,
    DeleteUserFollowView,
    EditReviewView,
    EditTicketView,
)

urlpatterns = [
    path("", FeedView.as_view(), name="feed"),
    path(
        "my-posts/",
        UserPostsView.as_view(),
        name="user_posts",
    ),

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
        "review/create/<int:pk>/",
        CreateReviewView.as_view(),
        name="review_create",
    ),
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
        "ticket_review/create/",
        CreateTicketAndReviewView.as_view(),
        name="create_ticket_review",
    ),
    path(
        "subscriptions/",
        CreateUserFollowsView.as_view(),
        name="subscriptions",
    ),
    path(
        "subscription/delete/<int:pk>/",
        DeleteUserFollowView.as_view(),
        name="subscription_delete",
    ),
]
