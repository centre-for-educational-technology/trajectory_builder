from django import forms
from .models import StudentProfile
from django.contrib.auth.models import User

from users.forms import UpdateProfileForm, UpdateUserForm

class StudentProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['school_level', 'school_name', 'current_class']
        widgets = {
            'school_level': forms.Select(attrs={'class': 'form-control'}),
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'current_class': forms.TextInput(attrs={'class': 'form-control'}),
        }