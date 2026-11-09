from django.db import models
from django.utils import timezone
from patients.models import Patient
from appointment.models import Appointment
from usermanagement.models import CustomUser


class Invoice(models.Model):
    PAYMENT_STATUS = [
        ('unpaid',         'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('paid',           'Paid'),
        ('waived',         'Waived'),
        ('refunded',       'Refunded'),
    ]
    PAYMENT_MODE = [
        ('cash',   'Cash'),
        ('upi',    'UPI'),
        ('card',   'Card'),
        ('neft',   'NEFT/RTGS'),
        ('cheque', 'Cheque'),
        ('other',  'Other'),
    ]

    invoice_number   = models.CharField(max_length=30, unique=True)
    patient          = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    appointment      = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    created_by       = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='invoices_created')

    invoice_date     = models.DateField(default=timezone.now)
    due_date         = models.DateField(null=True, blank=True)

    subtotal         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid      = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status   = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_mode     = models.CharField(max_length=20, choices=PAYMENT_MODE, blank=True)
    payment_ref      = models.CharField(max_length=100, blank=True, help_text="UPI txn ID / cheque no")
    payment_date     = models.DateTimeField(null=True, blank=True)

    notes            = models.TextField(blank=True)
    is_first_visit   = models.BooleanField(default=False)

    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date', '-created_at']

    def __str__(self):
        return f"{self.invoice_number} | {self.patient} | ₹{self.total_amount}"

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def save(self, *args, **kwargs):
        self.subtotal     = sum(item.amount for item in self.items.all()) if self.pk else self.subtotal
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        if self.amount_paid >= self.total_amount and self.total_amount > 0:
            self.payment_status = 'paid'
        elif self.amount_paid > 0:
            self.payment_status = 'partially_paid'
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice      = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description  = models.CharField(max_length=300)
    category     = models.CharField(max_length=50, blank=True)
    quantity     = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_rate    = models.DecimalField(max_digits=10, decimal_places=2)
    amount       = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x{self.quantity} = ₹{self.amount}"


class Payment(models.Model):
    """Record of payment transactions against an invoice"""
    invoice      = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    mode         = models.CharField(max_length=20, choices=Invoice.PAYMENT_MODE)
    reference    = models.CharField(max_length=100, blank=True)
    paid_at      = models.DateTimeField(default=timezone.now)
    received_by  = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    notes        = models.TextField(blank=True)

    def __str__(self):
        return f"₹{self.amount} via {self.mode} for {self.invoice.invoice_number}"
