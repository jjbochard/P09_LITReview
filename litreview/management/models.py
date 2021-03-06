from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Ticket(models.Model):
    title = models.CharField(max_length=128, verbose_name="titre")
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to="image")
    time_created = models.DateTimeField(auto_now_add=True)
    got_review = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Review(models.Model):
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        primary_key=False,
    )
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="note",
    )
    headline = models.CharField(max_length=128, verbose_name="titre")
    body = models.TextField(max_length=8192, blank=True, verbose_name="commentaire")
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.headline


class UserFollows(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_by",
    )

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-followed_user pairs
        unique_together = (
            "user",
            "followed_user",
        )
