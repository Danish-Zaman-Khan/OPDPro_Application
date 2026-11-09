from django.contrib import admin
from .models import LabReport

@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'report_type', 'title', 'report_date', 'status', 'lab_name']
    list_filter   = ['report_type', 'status', 'report_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'title']
