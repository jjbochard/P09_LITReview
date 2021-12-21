from django.forms import ModelForm

from .models import Ticket


class TicketForm(ModelForm):
    # def __init__(self, user, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.user = user

    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]
