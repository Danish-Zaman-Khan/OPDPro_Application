from django.db import models
from patients.models import Patient
from appointment.models import Appointment
from usermanagement.models import CustomUser


# ── Indian drug master list ──────────────────────────────────────────────────
class DrugMaster(models.Model):
    FORM_CHOICES = [
        ('tablet','Tablet'), ('capsule','Capsule'), ('syrup','Syrup'),
        ('injection','Injection'), ('drops','Drops'), ('ointment','Ointment'),
        ('inhaler','Inhaler'), ('powder','Powder'), ('sachet','Sachet'),
        ('suspension','Suspension'), ('cream','Cream'), ('gel','Gel'), ('other','Other'),
    ]
    name          = models.CharField(max_length=200)
    generic_name  = models.CharField(max_length=200, blank=True)
    form          = models.CharField(max_length=20, choices=FORM_CHOICES, default='tablet')
    strength      = models.CharField(max_length=50, blank=True, help_text="e.g. 500mg, 250mg/5ml")
    manufacturer  = models.CharField(max_length=200, blank=True)
    is_active     = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        s = self.name
        if self.strength: s += f" {self.strength}"
        if self.form: s += f" ({self.form})"
        return s


# ── Prescription ─────────────────────────────────────────────────────────────
class Prescription(models.Model):
    STATUS_CHOICES = [
        ('draft',      'Draft'),
        ('issued',     'Issued'),
        ('dispensed',  'Dispensed by Pharmacy'),
        ('cancelled',  'Cancelled'),
    ]
    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    appointment      = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    doctor           = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='prescriptions_written')
    dispensed_by     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions_dispensed')

    date             = models.DateField(auto_now_add=True)
    chief_complaint  = models.TextField(blank=True)
    diagnosis        = models.CharField(max_length=300, blank=True)
    advice           = models.TextField(blank=True, help_text="General advice / lifestyle notes")
    follow_up_days   = models.IntegerField(null=True, blank=True, help_text="Follow-up in N days")
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    dispensed_at     = models.DateTimeField(null=True, blank=True)
    pharmacist_notes = models.TextField(blank=True)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Rx-{self.pk} | {self.patient} | {self.date}"


class PrescriptionItem(models.Model):
    FREQUENCY_CHOICES = [
        ('OD',    'Once Daily (OD)'),
        ('BD',    'Twice Daily (BD)'),
        ('TDS',   'Thrice Daily (TDS)'),
        ('QID',   'Four Times Daily (QID)'),
        ('SOS',   'As Needed (SOS)'),
        ('HS',    'At Bedtime (HS)'),
        ('AC',    'Before Meals (AC)'),
        ('PC',    'After Meals (PC)'),
        ('STAT',  'Immediately (STAT)'),
        ('OW',    'Once a Week'),
        ('BW',    'Twice a Week'),
    ]
    DURATION_UNIT = [
        ('days','Days'), ('weeks','Weeks'), ('months','Months'), ('ongoing','Ongoing'),
    ]
    prescription   = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    drug           = models.ForeignKey(DrugMaster, on_delete=models.SET_NULL, null=True, blank=True)
    drug_name      = models.CharField(max_length=200, help_text="Free-text if not in master")
    strength       = models.CharField(max_length=50, blank=True)
    form           = models.CharField(max_length=50, blank=True)
    dose           = models.CharField(max_length=50, blank=True, help_text="e.g. 1 tab, ½ tab, 5ml")
    frequency      = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='OD')
    duration       = models.IntegerField(default=5)
    duration_unit  = models.CharField(max_length=10, choices=DURATION_UNIT, default='days')
    route          = models.CharField(max_length=50, blank=True, default='Oral')
    instructions   = models.CharField(max_length=200, blank=True, help_text="e.g. with warm water, after food")
    quantity       = models.IntegerField(default=0, help_text="Total tablets/units to dispense")
    dispensed_qty  = models.IntegerField(default=0)
    sort_order     = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.drug_name} {self.frequency} x {self.duration} {self.duration_unit}"
