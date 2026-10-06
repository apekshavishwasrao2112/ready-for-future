from django import forms

from .models import Resume


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['resume_file']
        widgets = {
            'resume_file': forms.ClearableFileInput(
                attrs={'accept': '.pdf'}
            )
        }
        help_texts = {
            'resume_file': 'Choose a PDF resume.'
        }
