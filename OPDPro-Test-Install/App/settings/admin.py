from django.contrib import admin
from .models import ClinicSettings, FeeItem

@admin.register(ClinicSettings)
class ClinicSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ClinicSettings.objects.exists()

@admin.register(FeeItem)
class FeeItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'default_rate', 'unit', 'is_active']
    list_editable = ['is_active']
