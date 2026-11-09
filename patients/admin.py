from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 
        'last_name', 
        'date_of_birth', 
        'gender', 
        'phone_number',
        'email',
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('gender', 'date_of_birth')
    ordering = ('last_name', 'first_name')
