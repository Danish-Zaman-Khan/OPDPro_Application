from django.db import models


class ClinicSettings(models.Model):
    """Single-row clinic configuration"""
    clinic_name        = models.CharField(max_length=200, default="My Clinic")
    clinic_tagline     = models.CharField(max_length=300, blank=True)
    address_line1      = models.CharField(max_length=200, blank=True)
    address_line2      = models.CharField(max_length=200, blank=True)
    city               = models.CharField(max_length=100, default="Mumbai")
    state              = models.CharField(max_length=100, default="Maharashtra")
    pincode            = models.CharField(max_length=10, blank=True)
    phone              = models.CharField(max_length=20, blank=True)
    email              = models.EmailField(blank=True)
    gstin              = models.CharField(max_length=20, blank=True, verbose_name="GSTIN")
    registration_no    = models.CharField(max_length=100, blank=True)

    # OPD Visit fee defaults (auto-charge on first visit)
    opd_consultation_fee   = models.DecimalField(max_digits=8, decimal_places=2, default=300)
    revisit_fee            = models.DecimalField(max_digits=8, decimal_places=2, default=150)
    emergency_fee          = models.DecimalField(max_digits=8, decimal_places=2, default=500)
    revisit_days           = models.IntegerField(default=7, help_text="Days within which a visit counts as revisit")

    # Invoice
    invoice_prefix         = models.CharField(max_length=10, default="INV")
    invoice_footer_note    = models.TextField(blank=True, default="Thank you for visiting. Please follow doctor's advice.")

    updated_at             = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clinic Settings"

    def __str__(self):
        return self.clinic_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FeeItem(models.Model):
    """Customizable fee catalogue"""
    CATEGORY_CHOICES = [
        ('consultation', 'Consultation'),
        ('procedure',    'Procedure'),
        ('lab',          'Laboratory'),
        ('radiology',    'Radiology'),
        ('medicine',     'Medicine'),
        ('other',        'Other'),
    ]
    name         = models.CharField(max_length=200)
    category     = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    default_rate = models.DecimalField(max_digits=10, decimal_places=2)
    unit         = models.CharField(max_length=30, default='per visit')
    is_active    = models.BooleanField(default=True)
    description  = models.TextField(blank=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (₹{self.default_rate})"
