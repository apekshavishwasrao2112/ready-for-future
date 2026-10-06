from django.contrib.auth.models import User
from django.db import models


class LearningProgress(models.Model):
    FRESHER = 'fresher'
    EXPERIENCED = 'experienced'
    ROADMAP_CHOICES = [
        (FRESHER, 'Fresher'),
        (EXPERIENCED, 'Experienced'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='learning_progress'
    )
    roadmap_type = models.CharField(
        max_length=20,
        choices=ROADMAP_CHOICES
    )
    day_number = models.PositiveSmallIntegerField()
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'roadmap_type', 'day_number'],
                name='unique_learning_day_per_user'
            )
        ]

    def __str__(self):
        return f'{self.user.username}: {self.roadmap_type} day {self.day_number}'
