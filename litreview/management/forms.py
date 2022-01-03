from django.forms import ModelForm

from .models import Review, Ticket


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]
