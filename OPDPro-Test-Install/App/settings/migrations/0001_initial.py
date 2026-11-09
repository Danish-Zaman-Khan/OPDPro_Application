from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='ClinicSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('clinic_name', models.CharField(default='My Clinic', max_length=200)),
                ('clinic_tagline', models.CharField(blank=True, max_length=300)),
                ('address_line1', models.CharField(blank=True, max_length=200)),
                ('address_line2', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(default='Mumbai', max_length=100)),
                ('state', models.CharField(default='Maharashtra', max_length=100)),
                ('pincode', models.CharField(blank=True, max_length=10)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('gstin', models.CharField(blank=True, max_length=20, verbose_name='GSTIN')),
                ('registration_no', models.CharField(blank=True, max_length=100)),
                ('opd_consultation_fee', models.DecimalField(decimal_places=2, default=300, max_digits=8)),
                ('revisit_fee', models.DecimalField(decimal_places=2, default=150, max_digits=8)),
                ('emergency_fee', models.DecimalField(decimal_places=2, default=500, max_digits=8)),
                ('revisit_days', models.IntegerField(default=7)),
                ('invoice_prefix', models.CharField(default='INV', max_length=10)),
                ('invoice_footer_note', models.TextField(blank=True, default='Thank you for visiting.')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'verbose_name': 'Clinic Settings'},
        ),
        migrations.CreateModel(
            name='FeeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(choices=[('consultation','Consultation'),('procedure','Procedure'),('lab','Laboratory'),('radiology','Radiology'),('medicine','Medicine'),('other','Other')], default='other', max_length=30)),
                ('default_rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unit', models.CharField(default='per visit', max_length=30)),
                ('is_active', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={'ordering': ['category', 'name']},
        ),
    ]
