# forms.py

from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 
            'last_name', 
            'gender', 
            'mobile_number', 
            'email', 
            'photo', 
            'date_of_birth', 
            'address',
        ]
