from crispy_forms.bootstrap import InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms
from django.forms import ModelForm

from .models import Review, Ticket


class TicketForm(ModelForm):
    class Meta:
        model = Ticket
        fields = ["title", "description", "image"]


RATINGS = [
    ("0", 0),
    ("1", 1),
    ("2", 2),
    ("3", 3),
    ("4", 4),
    ("5", 5),
]


class ReviewForm(ModelForm):

    rating = forms.ChoiceField(choices=RATINGS, widget=forms.RadioSelect, label="Note")

    class Meta:
        model = Review
        fields = ["headline", "rating", "body"]

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields["rating"].required = True
        self.helper = FormHelper()
        self.helper.layout = Layout(
            "headline",
            Div(InlineRadios("rating")),
            "body",
        )
