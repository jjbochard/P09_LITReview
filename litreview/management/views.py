from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import TicketForm
from .models import Ticket


def index(request):
    tickets = Ticket.objects.all()
    context = {"tickets": tickets}
    return render(request, "management/tickets_list.html", context)


class CreateTicketView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "management/ticket_create.html"
    success_url = reverse_lazy("index")

    def post(self, request):
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def get_success_url(self):
        return self.success_url

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({"user": self.request.user.id})
    #     print(kwargs)
    #     return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
