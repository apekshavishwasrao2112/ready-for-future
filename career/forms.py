from django import forms
from .models import CareerProfile


class CareerProfileForm(forms.ModelForm):

    class Meta:
        model = CareerProfile

        fields = [
            'full_name',
            'current_role',
            'experience_level',
            'target_role',
            'skills',
        ]

        widgets = {

            'full_name': forms.TextInput(
                attrs={
                    'placeholder': 'Your full name'
                }
            ),

            'current_role': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. Python Full Stack Developer'
                }
            ),

            'target_role': forms.TextInput(
                attrs={
                    'placeholder': 'e.g. AI Engineer'
                }
            ),

            'skills': forms.Textarea(
                attrs={
                    'placeholder': 'Python, Django, React, SQL...',
                    'rows': 4
                }
            ),
        }