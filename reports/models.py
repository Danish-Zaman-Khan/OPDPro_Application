from django.db import models
from django.utils import timezone
from patients.models import Patient
from appointment.models import Appointment
from usermanagement.models import CustomUser
import os


def report_upload_path(instance, filename):
    return f"reports/patient_{instance.patient_id}/{instance.report_type}/{filename}"


class LabReport(models.Model):
    REPORT_TYPE = [
        ('blood',      'Blood Test'),
        ('urine',      'Urine Test'),
        ('stool',      'Stool Test'),
        ('xray',       'X-Ray'),
        ('ecg',        'ECG'),
        ('echo',       'Echo / Ultrasound'),
        ('mri',        'MRI / CT Scan'),
        ('culture',    'Culture / Sensitivity'),
        ('biopsy',     'Biopsy'),
        ('pathology',  'Pathology'),
        ('other',      'Other'),
    ]
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('in_process', 'In Process'),
        ('completed',  'Completed'),
        ('reviewed',   'Reviewed by Doctor'),
    ]

    patient        = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_reports')
    appointment    = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_reports')
    ordered_by     = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='reports_ordered')
    uploaded_by    = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_uploaded')
    reviewed_by    = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')

    report_type    = models.CharField(max_length=20, choices=REPORT_TYPE)
    title          = models.CharField(max_length=300)
    lab_name       = models.CharField(max_length=200, blank=True)
    report_date    = models.DateField(default=timezone.now)
    file           = models.FileField(upload_to=report_upload_path, null=True, blank=True)
    notes          = models.TextField(blank=True, help_text="Lab technician notes / abnormal values")
    doctor_remarks = models.TextField(blank=True)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-report_date', '-created_at']

    def __str__(self):
        return f"{self.get_report_type_display()} | {self.patient} | {self.report_date}"

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else None
