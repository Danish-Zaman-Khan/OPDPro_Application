from datetime import datetime, date
from django.utils import timezone
from django.db import models
from patients.models import Patient
from usermanagement.models import CustomUser  # assuming your custom user model is here

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    referred_doctor = models.CharField(max_length=50, blank=True, null=True, default='NA')
    date = models.DateField()
    time = models.TimeField()
    appointment_reason = models.TextField(blank=True, null=True)  # fixed typo
    doctor_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Missed', 'Missed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"Appointment with {self.patient} on {self.date} at {self.time}"

    @property
    def effective_status(self):
        today = date.today()
        if self.status in ['Completed', 'Cancelled']:
            return self.status
        elif self.date == today:
            return 'Pending'
        elif self.date < today:
            return 'Missed'
        return 'Scheduled'

    def get_dynamic_status(self):
        if self.status in ['Completed', 'Cancelled']:
            return self.status

        appointment_datetime = timezone.make_aware(datetime.combine(self.date, self.time))
        now = timezone.now()

        if appointment_datetime.date() == now.date() and appointment_datetime > now:
            return 'Pending'
        elif appointment_datetime < now:
            return 'Missed'
        else:
            return 'Scheduled'
