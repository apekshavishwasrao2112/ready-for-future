from django.contrib import admin

from .models import CareerTaskProgress, LearningProgress


admin.site.register(LearningProgress)
admin.site.register(CareerTaskProgress)
