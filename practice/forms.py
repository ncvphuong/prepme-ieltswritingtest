"""
Forms for the practice app.
"""
from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    """Form for creating and editing submissions."""
    
    class Meta:
        model = Submission
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control writing-textarea',
                'rows': 20,
                'placeholder': 'Start writing your response here...',
                'data-autosave': 'true',
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False