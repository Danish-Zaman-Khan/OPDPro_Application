from django import forms
from usermanagement.models import CustomUser

class DoctorEditForm(forms.ModelForm):
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