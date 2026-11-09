from django.shortcuts import render, get_object_or_404, redirect
from .models import Appointment
from patients.models import Patient
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm, DoctorNotesForm
from django.contrib import messages
from rest_framework import viewsets
from .serializers import AppointmentSerializer
from datetime import timedelta


def mark_missed_appointments():
    now = timezone.now()
    Appointment.objects.filter(date__lt=now.date(), status='Pending').update(status='Missed')
    Appointment.objects.filter(date=now.date(), time__lt=now.time(), status='Pending').update(status='Missed')


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if appointment.doctor != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to cancel this appointment.")
        return redirect('usermanagement:dashboard')
    appointment.status = 'Cancelled'
    appointment.save()
    messages.success(request, "Appointment cancelled.")
    return redirect('usermanagement:dashboard')


@login_required
def appointment_list(request):
    mark_missed_appointments()
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-date', '-time')
    return render(request, 'appointment/appointmentlist.html', {'appointments': appointments})


@login_required
def today_appointments(request):
    mark_missed_appointments()
    today = timezone.now().date()
    appointments = Appointment.objects.filter(doctor=request.user, date=today).order_by('time')
    return render(request, 'appointment/today_appointments.html', {'appointments': appointments})


@login_required
def upcoming_appointments(request):
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    seven_days_later = today + timedelta(days=7)
    appointments = Appointment.objects.filter(
        doctor=request.user,
        date__range=[tomorrow, seven_days_later]
    ).order_by('date', 'time')
    return render(request, 'appointment/upcoming_appointments.html', {'appointments': appointments})


@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = request.user
            appointment.save()
            messages.success(request, "Appointment booked successfully!")
            return redirect('appointment:appointment_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm()
    return render(request, 'appointment/bookappointmentdoctor.html', {'form': form})


@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect('appointment:appointment_detail', pk=appointment_id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointment/editappointment.html', {'form': form, 'appointment': appointment})


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointment/appointmentdetails.html', {'appointment': appointment})


@login_required
def appointment_viewdetail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointment/appointmentdetailsview.html', {'appointment': appointment})


@login_required
def visit_history(request, patient_id):
    visit_history = Appointment.objects.filter(patient__id=patient_id).order_by('-date', '-time')
    return render(request, 'appointment/appointmentHistory.html', {'visit_history': visit_history})


@login_required
def edit_doctor_notes(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        form = DoctorNotesForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Notes updated successfully.")
            return redirect('appointment:appointment_detail', pk=appointment.pk)
    else:
        form = DoctorNotesForm(instance=appointment)
    return render(request, 'appointment/edit_doctor_notes.html', {'form': form, 'appointment': appointment})


@login_required
def mark_completed(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        appointment.status = "Completed"
        appointment.save()
        messages.success(request, "Appointment marked as completed.")
    return redirect('appointment:appointment_detail', pk=pk)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
