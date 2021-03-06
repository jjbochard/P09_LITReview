from itertools import chain

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.db.models import CharField, Q, Value
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import ReviewForm, TicketForm, UserFollowForm
from .models import Review, Ticket, UserFollows


class FeedView(LoginRequiredMixin, TemplateView):

    template_name = "management/feed/feed.html"

    def get_context_data(self, **kwargs):
        # Get users.id request.user follows
        followed_users_id = UserFollows.objects.filter(
            user=self.request.user
        ).values_list("followed_user_id", flat=True)

        # Get reviews make by them and annotate
        reviews_followed_users = (
            Review.objects.filter(
                Q(user__in=followed_users_id) | Q(user=self.request.user.id)
            ).select_related()
        ).annotate(content_type=Value("REVIEW", CharField()))

        # Get tickets make by them and annotate
        tickets_followed_users = (
            Ticket.objects.filter(
                Q(user__in=followed_users_id) | Q(user=self.request.user.id)
            ).select_related()
        ).annotate(content_type=Value("TICKET", CharField()))

        # get users.id whos follow request.user
        following_users_id = UserFollows.objects.filter(
            followed_user=self.request.user
        ).values_list("user_id", flat=True)
        # Get reviews make by them for request.user tickets and annotate
        reviews_following_users = (
            Review.objects.filter(
                Q(user__in=following_users_id) & Q(ticket__user=self.request.user.id)
            )
            .select_related()
            .annotate(content_type=Value("REVIEW", CharField()))
        )

        # Put together and sort their reviews and tickets
        # Use set to not have duplicate reviews or tickets
        posts = sorted(
            set(
                chain(
                    reviews_followed_users,
                    tickets_followed_users,
                    reviews_following_users,
                )
            ),
            key=lambda post: post.time_created,
            reverse=True,
        )
        return {
            "feed_posts": posts,
            "current_user": self.request.user.id,
        }


class UserPostsView(LoginRequiredMixin, TemplateView):
    template_name = "management/user_posts/user_posts.html"

    def get_context_data(self, **kwargs):
        reviews = (
            Review.objects.filter(user=self.request.user)
            .select_related()
            .annotate(content_type=Value("REVIEW", CharField()))
        )

        # get tickets make by them
        tickets = (
            Ticket.objects.filter(user=self.request.user)
            .select_related()
            .annotate(content_type=Value("TICKET", CharField()))
        )

        # Put together and sort their reviews and tickets
        posts = sorted(
            chain(reviews, tickets), key=lambda post: post.time_created, reverse=True
        )
        return {"user_posts": posts}


class CreateUserFollowsView(LoginRequiredMixin, CreateView):
    model = UserFollows
    form_class = UserFollowForm
    template_name = "management/subscriptions_list.html"

    def get_success_url(self):
        return reverse_lazy("subscriptions")

    def get_form_kwargs(self):
        kwargs = super(CreateUserFollowsView, self).get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def post(self, request):
        form = UserFollowForm(user=self.request.user, data=request.POST)
        form.instance.user = self.request.user
        if form.is_valid():
            try:
                form.save()
            except IntegrityError:
                messages.add_message(
                    request, messages.INFO, "Vous suivez d??j?? cet utilisateur."
                )
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_follows = UserFollows.objects.all().select_related()
        context["current_user"] = self.request.user
        context["following_users"] = sorted(
            user_follows,
            key=lambda user: user.user.username,
            reverse=False,
        )
        context["followed_users"] = sorted(
            user_follows,
            key=lambda user: user.followed_user.username,
            reverse=False,
        )
        return context


class CreateTicketView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "management/tickets/ticket_create.html"

    def post(self, request):
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("feed")


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

    def post(self, request, *args, **kwargs):
        form = ReviewForm(request.POST)

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("feed")

    def form_valid(self, form):
        form.instance.user = self.request.user
        ticket = Ticket.objects.get(pk=self.kwargs["pk"])
        ticket.got_review = True
        ticket.save()
        review = form.save(commit=False)
        review.ticket = ticket
        review.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["ticket"] = Ticket.objects.select_related().get(pk=self.kwargs["pk"])
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

    def get_success_url(self):
        return reverse_lazy("user_posts")


class DeleteReviewView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "management/reviews/review_delete.html"
    model = Review

    def test_func(self):
        return self.get_object().user == self.request.user

    def form_valid(self, form):
        review = Review.objects.get(pk=self.kwargs["pk"])
        ticket_review = review.ticket.id
        ticket = Ticket.objects.get(pk=ticket_review)
        ticket.got_review = False
        ticket.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("user_posts")


class CreateTicketAndReviewView(LoginRequiredMixin, TemplateView):

    # Initalize our two forms here with separate prefixes
    template_name = "management/reviews/create_ticket_and_review.html"

    def post(self, request, *args, **kwargs):
        form = TicketForm(request.POST, request.FILES, prefix="ticket")
        sub_form = ReviewForm(request.POST, prefix="review")
        form.instance.user = self.request.user

        if form.is_valid() and sub_form.is_valid():
            form.instance.user = self.request.user
            sub_form.instance.user = self.request.user
            ticket = form.save(commit=False)
            ticket.got_review = True
            ticket.save()
            review = sub_form.save(commit=False)
            review.ticket = form.save()
            review.save()

        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        form = TicketForm(prefix="ticket")
        sub_form = ReviewForm(prefix="review")

        return {"form": form, "sub_form": sub_form}

    def get_success_url(self):
        return reverse_lazy("feed")


class DeleteUserFollowView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "management/subscription_delete.html"
    model = UserFollows

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_success_url(self):
        return reverse_lazy("subscriptions")
