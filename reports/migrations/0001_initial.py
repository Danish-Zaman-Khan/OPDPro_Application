from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion, django.utils.timezone
import reports.models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('patients', '0002_alter_patient_full_name'),
        ('appointment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='LabReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('report_type', models.CharField(choices=[('blood','Blood Test'),('urine','Urine Test'),('stool','Stool Test'),('xray','X-Ray'),('ecg','ECG'),('echo','Echo / Ultrasound'),('mri','MRI / CT Scan'),('culture','Culture / Sensitivity'),('biopsy','Biopsy'),('pathology','Pathology'),('other','Other')], max_length=20)),
                ('title', models.CharField(max_length=300)),
                ('lab_name', models.CharField(blank=True, max_length=200)),
                ('report_date', models.DateField(default=django.utils.timezone.now)),
                ('file', models.FileField(blank=True, null=True, upload_to=reports.models.report_upload_path)),
                ('notes', models.TextField(blank=True)),
                ('doctor_remarks', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending','Pending'),('in_process','In Process'),('completed','Completed'),('reviewed','Reviewed by Doctor')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab_reports', to='patients.patient')),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lab_reports', to='appointment.appointment')),
                ('ordered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_ordered', to=settings.AUTH_USER_MODEL)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_uploaded', to=settings.AUTH_USER_MODEL)),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_reviewed', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-report_date', '-created_at']},
        ),
    ]
