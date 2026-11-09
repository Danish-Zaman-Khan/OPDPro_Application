from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class GenderChoices(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')

BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=150, blank=True, unique= True)

    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GenderChoices.choices)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    blood_type = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        null=True,
        verbose_name="Blood Type"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.first_name and self.last_name:
            base_full_name = f"{self.first_name.strip()} {self.last_name.strip()}"
            unique_full_name = base_full_name
            counter = 1

            while Patient.objects.filter(full_name=unique_full_name).exclude(pk=self.pk).exists():
                unique_full_name = f"{base_full_name} ({counter})"
                counter += 1

            self.full_name = unique_full_name

        super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse("patient_detail", kwargs={"pk": self.pk})
