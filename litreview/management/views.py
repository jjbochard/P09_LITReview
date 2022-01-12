from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.db.models import CharField, Value
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ReviewForm, TicketForm, UserFollowForm
from .models import Review, Ticket, UserFollows


@login_required
def feed(request):
    # Get users request.user follows
    followed_users = UserFollows.objects.filter(user=request.user)
    # Get id for them
    followed_users_id = [user.followed_user_id for user in followed_users]
    # Add current user in this list
    followed_users_id.append(request.user.id)
    # Get reviews make by them
    reviews = Review.objects.filter(user__in=followed_users_id)
    reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))

    # get tickets make by them
    tickets = Ticket.objects.filter(user__in=followed_users_id)
    tickets = tickets.annotate(content_type=Value("TICKET", CharField()))

    # Put together and sort their reviews and tickets
    posts = sorted(
        chain(reviews, tickets), key=lambda post: post.time_created, reverse=True
    )
    return render(
        request,
        "management/feed/feed.html",
        context={"feed_posts": posts, "current_user": request.user.id},
    )


@login_required
def user_posts(request):
    reviews = Review.objects.filter(user=request.user)
    reviews = reviews.annotate(content_type=Value("REVIEW", CharField()))

    # get tickets make by them
    tickets = Ticket.objects.filter(user=request.user)
    tickets = tickets.annotate(content_type=Value("TICKET", CharField()))

    # Put together and sort their reviews and tickets
    posts = sorted(
        chain(reviews, tickets), key=lambda post: post.time_created, reverse=True
    )
    return render(
        request, "management/user_posts/user_posts.html", context={"user_posts": posts}
    )


class CreateUserFollowsView(LoginRequiredMixin, TemplateView):

    template_name = "management/subscriptions_list.html"

    def get_success_url(self):
        return reverse_lazy("subscriptions")

    def post(self, request, *args, **kwargs):
        form = UserFollowForm(request.POST)
        form.instance.user = self.request.user
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                messages.add_message(
                    request, messages.INFO, "Vous suivez déjà cet utilisateur."
                )

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        form = UserFollowForm
        user_follows = UserFollows.objects.all()
        current_user = self.request.user
        following_users = sorted(
            user_follows,
            key=lambda user: user.user.username,
            reverse=False,
        )
        followed_users = sorted(
            user_follows,
            key=lambda user: user.followed_user.username,
            reverse=False,
        )
        return {
            "form": form,
            "followed_users": followed_users,
            "following_users": following_users,
            "current_user": current_user,
        }


class CreateTicketView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "management/tickets/ticket_create.html"
    success_url = reverse_lazy("feed")

    def post(self, request):
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def get_success_url(self):
        return self.success_url

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditTicketView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = "management/tickets/ticket_edit.html"

    def test_func(self):
        return self.get_object().user == self.request.user

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
        return reverse_lazy("user_posts")


class DeleteTicketView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "management/tickets/ticket_delete.html"
    model = Ticket

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):

        return reverse_lazy("user_posts")


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = "management/reviews/review_create.html"
    success_url = reverse_lazy("feed")

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


class EditReviewView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "management/reviews/review_edit.html"

    def test_func(self):
        return self.get_object().user == self.request.user

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
        return reverse_lazy("user_posts")


class DeleteReviewView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "management/reviews/review_delete.html"
    model = Review

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):

        return reverse_lazy("user_posts")


class CreateTicketAndReviewView(LoginRequiredMixin, TemplateView):

    # Initalize our two forms here with separate prefixes
    template_name = "management/reviews/create_ticket_and_review.html"

    def get_success_url(self):
        return reverse_lazy("feed")

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


class DeleteUserFollowView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "management/subscription_delete.html"
    model = UserFollows

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse_lazy("subscriptions")
