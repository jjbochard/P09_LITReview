from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ReviewForm, TicketForm
from .models import Review, Ticket


def index(request):
    tickets = Ticket.objects.all()
    context = {"tickets": tickets}
    return render(request, "management/tickets/tickets_list.html", context)


def ReviewList(request):
    reviews = Review.objects.all()
    context = {"reviews": reviews}
    return render(request, "management/reviews/reviews_list.html", context)


class CreateTicketView(CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "management/tickets/ticket_create.html"
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


class EditTicketView(UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = "management/tickets/ticket_edit.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = TicketForm(request.POST, request.FILES, instance=self.object)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("index")

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs.update({"user": self.request.user.id})
    #     print(kwargs)
    #     return kwargs


class DeleteTicketView(DeleteView):
    template_name = "management/tickets/ticket_delete.html"
    model = Ticket

    def get_success_url(self):

        return reverse_lazy("index")


class CreateReviewView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "management/reviews/review_create.html"
    success_url = reverse_lazy("reviews_list")

    def post(self, request, *args, **kwargs):
        form = ReviewForm(request.POST)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        form.instance.user = self.request.user
        ticket = Ticket.objects.get(pk=self.kwargs["pk"])
        review = form.save(commit=False)
        review.ticket = ticket
        review.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["ticket"] = Ticket.objects.get(pk=self.kwargs["pk"])
        print(context)
        return context


class EditReviewView(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "management/reviews/review_edit.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ReviewForm(request.POST, request.FILES, instance=self.object)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        review = form.save(commit=False)
        review.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("reviews_list")


class DeleteReviewView(DeleteView):
    template_name = "management/reviews/review_delete.html"
    model = Review

    def get_success_url(self):

        return reverse_lazy("reviews_list")
