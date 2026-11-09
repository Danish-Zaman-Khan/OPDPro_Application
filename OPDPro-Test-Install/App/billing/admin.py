from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display  = ['invoice_number', 'patient', 'invoice_date', 'total_amount', 'amount_paid', 'payment_status']
    list_filter   = ['payment_status', 'invoice_date']
    search_fields = ['invoice_number', 'patient__first_name', 'patient__last_name']
    inlines       = [InvoiceItemInline, PaymentInline]
