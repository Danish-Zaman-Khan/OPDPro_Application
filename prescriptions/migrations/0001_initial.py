from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0002_alter_patient_full_name'),
        ('appointment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='DrugMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('generic_name', models.CharField(blank=True, max_length=200)),
                ('form', models.CharField(choices=[('tablet','Tablet'),('capsule','Capsule'),('syrup','Syrup'),('injection','Injection'),('drops','Drops'),('ointment','Ointment'),('inhaler','Inhaler'),('powder','Powder'),('sachet','Sachet'),('suspension','Suspension'),('cream','Cream'),('gel','Gel'),('other','Other')], default='tablet', max_length=20)),
                ('strength', models.CharField(blank=True, max_length=50)),
                ('manufacturer', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('chief_complaint', models.TextField(blank=True)),
                ('diagnosis', models.CharField(blank=True, max_length=300)),
                ('advice', models.TextField(blank=True)),
                ('follow_up_days', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('draft','Draft'),('issued','Issued'),('dispensed','Dispensed by Pharmacy'),('cancelled','Cancelled')], default='draft', max_length=20)),
                ('dispensed_at', models.DateTimeField(blank=True, null=True)),
                ('pharmacist_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='patients.patient')),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescriptions', to='appointment.appointment')),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescriptions_written', to=settings.AUTH_USER_MODEL)),
                ('dispensed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prescriptions_dispensed', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-date', '-created_at']},
        ),
        migrations.CreateModel(
            name='PrescriptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('drug_name', models.CharField(max_length=200)),
                ('strength', models.CharField(blank=True, max_length=50)),
                ('form', models.CharField(blank=True, max_length=50)),
                ('dose', models.CharField(blank=True, max_length=50)),
                ('frequency', models.CharField(choices=[('OD','Once Daily (OD)'),('BD','Twice Daily (BD)'),('TDS','Thrice Daily (TDS)'),('QID','Four Times Daily (QID)'),('SOS','As Needed (SOS)'),('HS','At Bedtime (HS)'),('AC','Before Meals (AC)'),('PC','After Meals (PC)'),('STAT','Immediately (STAT)'),('OW','Once a Week'),('BW','Twice a Week')], default='OD', max_length=10)),
                ('duration', models.IntegerField(default=5)),
                ('duration_unit', models.CharField(choices=[('days','Days'),('weeks','Weeks'),('months','Months'),('ongoing','Ongoing')], default='days', max_length=10)),
                ('route', models.CharField(blank=True, default='Oral', max_length=50)),
                ('instructions', models.CharField(blank=True, max_length=200)),
                ('quantity', models.IntegerField(default=0)),
                ('dispensed_qty', models.IntegerField(default=0)),
                ('sort_order', models.IntegerField(default=0)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='prescriptions.prescription')),
                ('drug', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='prescriptions.drugmaster')),
            ],
            options={'ordering': ['sort_order', 'id']},
        ),
    ]
