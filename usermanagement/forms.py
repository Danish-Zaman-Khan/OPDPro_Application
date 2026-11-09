from django import forms
from .models import CustomUser


class UserUpdateProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'mobile_number',
            'specialization',
            'license_number',
        ]
