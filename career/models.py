from django.db import models
from django.contrib.auth.models import User


class CareerProfile(models.Model):

    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('junior', '1–2 Years'),
        ('mid', '3–5 Years'),
        ('senior', '5+ Years'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)

    current_role = models.CharField(
        max_length=100,
        blank=True
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES
    )

    target_role = models.CharField(
        max_length=100
    )

    skills = models.TextField(
        help_text="Enter your skills separated by commas"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.full_name