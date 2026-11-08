from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Q
from usermanagement.models import CustomUser
from .forms import DoctorEditForm


def doctors_list(request):
    query = request.GET.get('q', '').strip()
    doctors = CustomUser.objects.all()
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
    is_admin = request.user.is_staff and request.user.staff_role == 'admin'
    if request.user.pk != pk and not is_admin:
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
