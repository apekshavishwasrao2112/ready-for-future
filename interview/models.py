from django.db import models


class InterviewQuestion(models.Model):
    TOPIC_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('sql', 'SQL'),
        ('javascript', 'JavaScript'),
        ('hr', 'HR'),
    ]

    topic = models.CharField(
        max_length=20,
        choices=TOPIC_CHOICES
    )
    question = models.CharField(max_length=300)
    answer_tip = models.TextField()
    keywords = models.CharField(
        max_length=200,
        blank=True,
        help_text='Comma-separated words used to match career profiles.'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['topic', 'id']

    def __str__(self):
        return self.question
