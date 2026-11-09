from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from usermanagement.models import CustomUser
from .forms import DoctorEditForm


def doctors_list(request):
    query = request.GET.get('q', '').strip()
    doctors = CustomUser.objects.filter(is_active=True)
    if query:
        doctors = doctors.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    return render(request, 'doctors/doctorslist.html', {'doctors': doctors, 'query': query})


def doctor_detail(request, pk):
    doctor = get_object_or_404(CustomUser, pk=pk)
    return render(request, 'doctors/doctordetails.html', {'doctor': doctor})


@login_required
def doctor_edit(request, pk):
    if request.user.pk != pk and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to edit this profile.")
    doctor = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = DoctorEditForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctors:doctor_detail', pk=doctor.pk)
    else:
        form = DoctorEditForm(instance=doctor)
    return render(request, 'doctors/doctoredit.html', {'form': form, 'doctor': doctor})
