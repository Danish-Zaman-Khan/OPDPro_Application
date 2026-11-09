from django.contrib import admin
from .models import Appointment  # import your models here

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'time', 'status')  # customize fields shown in admin list view
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__name', 'doctor__name')  # adjust based on your model fields
    ordering = ('-date', 'time')
