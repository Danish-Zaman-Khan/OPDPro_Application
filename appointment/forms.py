from django import forms
from .models import Appointment
from django.utils import timezone
import datetime

# # Book When on the Reception
# class AppointmentForm(forms.ModelForm):
#     class Meta:
#         model = Appointment
#         fields = ['patient', 'doctor', 'date', 'time', 'reason', 'status']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'time': forms.TimeInput(attrs={'type': 'time'}),
#         }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'date', 'time', 'appointment_reason']  # Add or remove fields as needed
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        appointment_date = cleaned_data.get("date")
        appointment_time = cleaned_data.get("time")

        if appointment_date and appointment_time:
            appointment_datetime = datetime.datetime.combine(appointment_date, appointment_time)

            # Convert to aware datetime (timezone-aware)
            appointment_datetime = timezone.make_aware(appointment_datetime, timezone.get_current_timezone())

            if appointment_datetime < timezone.now():
                raise forms.ValidationError("You cannot book an appointment in the past.")

        return cleaned_data



# Only for editing doctor's notes
class DoctorNotesForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor_notes']
