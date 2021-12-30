from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ReviewForm, TicketForm
from .models import Review, Ticket, UserFollows


@login_required
def index(request):
    tickets = Ticket.objects.all()
    context = {"tickets": tickets}
    return render(request, "management/tickets/tickets_list.html", context)


@login_required
def ReviewList(request):
    reviews = Review.objects.all()
    context = {"reviews": reviews}
    return render(request, "management/reviews/reviews_list.html", context)


@login_required
def UsersList(request):
    users = UserFollows.objects.all()
    current_user = request.user
    context = {
        "users": users,
        "current_user": current_user,
    }
    return render(request, "management/users_list.html", context)


class CreateTicketView(LoginRequiredMixin, CreateView):
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


class EditTicketView(LoginRequiredMixin, UpdateView):
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


class DeleteTicketView(LoginRequiredMixin, DeleteView):
    template_name = "management/tickets/ticket_delete.html"
    model = Ticket

    def get_success_url(self):

        return reverse_lazy("index")


class CreateReviewView(LoginRequiredMixin, CreateView):
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
        return context


class EditReviewView(LoginRequiredMixin, UpdateView):
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


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    template_name = "management/reviews/review_delete.html"
    model = Review

    def get_success_url(self):

        return reverse_lazy("reviews_list")


class CreateTicketAndReviewView(LoginRequiredMixin, TemplateView):

    # Initalize our two forms here with separate prefixes
    template_name = "management/reviews/create_ticket_and_review.html"

    def get_success_url(self):
        return reverse_lazy("reviews_list")

    def post(self, request, *args, **kwargs):
        form = TicketForm(request.POST, request.FILES, prefix="ticket")
        sub_form = ReviewForm(request.POST, prefix="review")
        form.instance.user = self.request.user

        if form.is_valid() and sub_form.is_valid():
            form.instance.user = self.request.user
            sub_form.instance.user = self.request.user

            review = sub_form.save(commit=False)
            review.ticket = form.save()
            review.save()

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        form = TicketForm(prefix="ticket")
        sub_form = ReviewForm(prefix="review")

        return {"form": form, "sub_form": sub_form}


class DeleteUserFollowView(LoginRequiredMixin, DeleteView):
    template_name = "management/user_follow_delete.html"
    model = UserFollows

    def get_success_url(self):
        return reverse_lazy("users_list")
