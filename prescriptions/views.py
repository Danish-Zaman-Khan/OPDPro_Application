from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q

from .models import Prescription, PrescriptionItem, DrugMaster
from patients.models import Patient
from appointment.models import Appointment


@login_required
def prescription_list(request):
    qs = Prescription.objects.select_related('patient', 'doctor').all()
    # Pharmacists see only issued ones
    if hasattr(request.user, 'staff_role') and request.user.staff_role == 'pharmacist':
        qs = qs.filter(status__in=['issued', 'dispensed'])
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(patient__first_name__icontains=q) | Q(patient__last_name__icontains=q))
    return render(request, 'prescriptions/list.html', {'prescriptions': qs, 'q': q})


@login_required
def create_prescription(request, patient_id=None, appointment_id=None):
    patient = get_object_or_404(Patient, pk=patient_id) if patient_id else None
    appointment = get_object_or_404(Appointment, pk=appointment_id) if appointment_id else None
    if appointment and not patient:
        patient = appointment.patient

    drugs = DrugMaster.objects.filter(is_active=True).values('id','name','generic_name','form','strength')

    if request.method == 'POST':
        pid = request.POST.get('patient_id')
        patient = get_object_or_404(Patient, pk=pid)
        appt_id = request.POST.get('appointment_id')
        appt = Appointment.objects.filter(pk=appt_id).first() if appt_id else None

        rx = Prescription.objects.create(
            patient         = patient,
            appointment     = appt,
            doctor          = request.user,
            chief_complaint = request.POST.get('chief_complaint', ''),
            diagnosis       = request.POST.get('diagnosis', ''),
            advice          = request.POST.get('advice', ''),
            follow_up_days  = request.POST.get('follow_up_days') or None,
            status          = 'issued',
        )
        # Items
        drug_ids   = request.POST.getlist('drug_id[]')
        drug_names = request.POST.getlist('drug_name[]')
        strengths  = request.POST.getlist('strength[]')
        forms      = request.POST.getlist('form[]')
        doses      = request.POST.getlist('dose[]')
        freqs      = request.POST.getlist('frequency[]')
        durs       = request.POST.getlist('duration[]')
        dur_units  = request.POST.getlist('duration_unit[]')
        instructions = request.POST.getlist('instructions[]')
        qtys       = request.POST.getlist('quantity[]')

        for i, name in enumerate(drug_names):
            if not name.strip(): continue
            drug_obj = DrugMaster.objects.filter(pk=drug_ids[i]).first() if i < len(drug_ids) and drug_ids[i] else None
            PrescriptionItem.objects.create(
                prescription  = rx,
                drug          = drug_obj,
                drug_name     = name,
                strength      = strengths[i] if i < len(strengths) else '',
                form          = forms[i]     if i < len(forms)     else '',
                dose          = doses[i]     if i < len(doses)     else '',
                frequency     = freqs[i]     if i < len(freqs)     else 'OD',
                duration      = durs[i]      if i < len(durs)      else 5,
                duration_unit = dur_units[i] if i < len(dur_units) else 'days',
                instructions  = instructions[i] if i < len(instructions) else '',
                quantity      = qtys[i]      if i < len(qtys)      else 0,
                sort_order    = i,
            )
        messages.success(request, f"Prescription Rx-{rx.pk} issued.")
        return redirect('prescriptions:detail', pk=rx.pk)

    return render(request, 'prescriptions/create.html', {
        'patient': patient, 'appointment': appointment,
        'drugs': list(drugs),
        'rx_frequencies': PrescriptionItem.FREQUENCY_CHOICES,
        'patients': Patient.objects.all().order_by('first_name'),
        'appointments': Appointment.objects.filter(status__in=['Pending','Scheduled']).order_by('-date')[:50],
    })


@login_required
def prescription_detail(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    return render(request, 'prescriptions/detail.html', {'rx': rx})


@login_required
def prescription_print(request, pk):
    from settings.models import ClinicSettings
    rx  = get_object_or_404(Prescription, pk=pk)
    cfg = ClinicSettings.get_settings()
    return render(request, 'prescriptions/print.html', {'rx': rx, 'cfg': cfg})


@login_required
def dispense_prescription(request, pk):
    """Pharmacist marks as dispensed"""
    rx = get_object_or_404(Prescription, pk=pk)
    if request.method == 'POST':
        rx.status        = 'dispensed'
        rx.dispensed_by  = request.user
        rx.dispensed_at  = timezone.now()
        rx.pharmacist_notes = request.POST.get('notes', '')
        rx.save()
        messages.success(request, "Prescription marked as dispensed.")
    return redirect('prescriptions:detail', pk=pk)


@login_required
def drug_search_api(request):
    """AJAX endpoint for drug autocomplete"""
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse({'results': []})
    drugs = DrugMaster.objects.filter(
        Q(name__icontains=q) | Q(generic_name__icontains=q), is_active=True
    )[:15]
    results = [{'id': d.id, 'name': d.name, 'generic': d.generic_name,
                'form': d.form, 'strength': d.strength} for d in drugs]
    return JsonResponse({'results': results})
