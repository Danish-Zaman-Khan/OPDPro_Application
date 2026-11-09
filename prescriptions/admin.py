from django.contrib import admin
from .models import DrugMaster, Prescription, PrescriptionItem

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'date', 'diagnosis', 'status']
    list_filter  = ['status', 'date']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis']
    inlines      = [PrescriptionItemInline]

@admin.register(DrugMaster)
class DrugMasterAdmin(admin.ModelAdmin):
    list_display  = ['name', 'generic_name', 'form', 'strength', 'manufacturer', 'is_active']
    list_filter   = ['form', 'is_active']
    search_fields = ['name', 'generic_name']
    list_editable = ['is_active']
