from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models


class Resume(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='resumes'
    )
    resume_file = models.FileField(
        upload_to='resumes/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf']
            )
        ]
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.user.username} - {self.resume_file.name}'
