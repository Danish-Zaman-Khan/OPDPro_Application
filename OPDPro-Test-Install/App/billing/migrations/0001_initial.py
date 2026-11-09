from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion, django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0002_alter_patient_full_name'),
        ('appointment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('invoice_number', models.CharField(max_length=30, unique=True)),
                ('invoice_date', models.DateField(default=django.utils.timezone.now)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tax_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('payment_status', models.CharField(choices=[('unpaid','Unpaid'),('partially_paid','Partially Paid'),('paid','Paid'),('waived','Waived'),('refunded','Refunded')], default='unpaid', max_length=20)),
                ('payment_mode', models.CharField(blank=True, max_length=20)),
                ('payment_ref', models.CharField(blank=True, max_length=100)),
                ('payment_date', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('is_first_visit', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='patients.patient')),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='appointment.appointment')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-invoice_date', '-created_at']},
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=300)),
                ('category', models.CharField(blank=True, max_length=50)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=8)),
                ('unit_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='billing.invoice')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('mode', models.CharField(max_length=20)),
                ('reference', models.CharField(blank=True, max_length=100)),
                ('paid_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='billing.invoice')),
                ('received_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
