from django.urls import path

from litreview.users.views import signup

urlpatterns = [
    path("signup/", signup, name="signup"),
]
