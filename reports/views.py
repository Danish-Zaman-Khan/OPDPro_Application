from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import LabReport
from patients.models import Patient
from appointment.models import Appointment


@login_required
def report_list(request):
    qs = LabReport.objects.select_related('patient', 'ordered_by').all()
    q      = request.GET.get('q', '').strip()
    rtype  = request.GET.get('type', '')
    status = request.GET.get('status', '')
    if q:      qs = qs.filter(Q(patient__first_name__icontains=q) | Q(patient__last_name__icontains=q) | Q(title__icontains=q))
    if rtype:  qs = qs.filter(report_type=rtype)
    if status: qs = qs.filter(status=status)
    return render(request, 'reports/list.html', {
        'reports': qs, 'q': q, 'rtype': rtype, 'status': status,
        'report_types': LabReport.REPORT_TYPE,
        'status_choices': LabReport.STATUS_CHOICES,
    })


@login_required
def upload_report(request, patient_id=None, appointment_id=None):
    patient     = get_object_or_404(Patient, pk=patient_id) if patient_id else None
    appointment = get_object_or_404(Appointment, pk=appointment_id) if appointment_id else None

    if request.method == 'POST':
        pid    = request.POST.get('patient_id')
        pat    = get_object_or_404(Patient, pk=pid)
        appt   = Appointment.objects.filter(pk=request.POST.get('appointment_id')).first()
        f      = request.FILES.get('file')
        rep = LabReport.objects.create(
            patient     = pat,
            appointment = appt,
            ordered_by  = Appointment.objects.filter(pk=request.POST.get('appointment_id')).first().doctor if appt else request.user,
            uploaded_by = request.user,
            report_type = request.POST['report_type'],
            title       = request.POST['title'],
            lab_name    = request.POST.get('lab_name', ''),
            report_date = request.POST.get('report_date') or None,
            notes       = request.POST.get('notes', ''),
            file        = f,
            status      = 'completed' if f else 'pending',
        )
        messages.success(request, "Report uploaded.")
        return redirect('reports:detail', pk=rep.pk)

    return render(request, 'reports/upload.html', {
        'patient': patient, 'appointment': appointment,
        'report_types': LabReport.REPORT_TYPE,
        'patients': Patient.objects.all().order_by('first_name'),
        'appointments': Appointment.objects.filter(status__in=['Pending','Scheduled']).order_by('-date')[:50],
    })


@login_required
def report_detail(request, pk):
    rep = get_object_or_404(LabReport, pk=pk)
    if request.method == 'POST' and request.user.staff_role == 'doctor':
        rep.doctor_remarks = request.POST.get('doctor_remarks', '')
        rep.status         = 'reviewed'
        rep.reviewed_by    = request.user
        rep.save()
        messages.success(request, "Remarks saved.")
        return redirect('reports:detail', pk=pk)
    return render(request, 'reports/detail.html', {'report': rep})


@login_required
def patient_reports(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    reports = LabReport.objects.filter(patient=patient).order_by('-report_date')
    return render(request, 'reports/patient_reports.html', {'patient': patient, 'reports': reports})
