from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class StaffRoleChoices(models.TextChoices):
    DOCTOR      = 'doctor',      _('Doctor')
    RECEPTIONIST= 'receptionist',_('Receptionist')
    NURSE       = 'nurse',       _('Nurse')
    PHARMACIST  = 'pharmacist',  _('Pharmacist')
    LAB         = 'lab',         _('Lab Technician')
    ADMIN       = 'admin',       _('Admin')


class GenderChoices(models.TextChoices):
    MALE   = 'M', _('Male')
    FEMALE = 'F', _('Female')
    OTHER  = 'O', _('Other')


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username       = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email          = models.EmailField(unique=True)
    mobile_number  = models.CharField(max_length=15, blank=True, null=True)
    first_name     = models.CharField(max_length=30, blank=True)
    last_name      = models.CharField(max_length=30, blank=True)
    date_of_birth  = models.DateField(null=True, blank=True)
    gender         = models.CharField(max_length=1, choices=GenderChoices.choices, blank=True)
    staff_role     = models.CharField(max_length=20, choices=StaffRoleChoices.choices, null=True, blank=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    signature      = models.TextField(blank=True, null=True, help_text="Doctor signature text for prescriptions")
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    date_joined    = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}" if self.staff_role == 'doctor' else f"{self.first_name} {self.last_name}"

    def is_doctor(self):       return self.staff_role == StaffRoleChoices.DOCTOR
    def is_receptionist(self): return self.staff_role == StaffRoleChoices.RECEPTIONIST
    def is_pharmacist(self):   return self.staff_role == StaffRoleChoices.PHARMACIST
    def is_lab(self):          return self.staff_role == StaffRoleChoices.LAB
    def get_full_name(self):   return f"{self.first_name} {self.last_name}".strip()
    def formatted_mobile(self):return f"+91 {self.mobile_number}" if self.mobile_number else "N/A"
