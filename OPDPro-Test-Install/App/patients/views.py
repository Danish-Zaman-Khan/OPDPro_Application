from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Patient
from .forms import PatientForm
from rest_framework import viewsets
from .serializers import PatientSerializer


class PatientregisterView(CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patient/patientregistrationform.html'
    success_url = reverse_lazy('patients:patient_list')

    def form_valid(self, form):
        messages.success(self.request, "Patient registered successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class PatientDetailView(DetailView):
    model = Patient
    template_name = 'patient/patientdetails.html'
    context_object_name = 'patient'


class PatientListView(ListView):
    model = Patient
    template_name = 'patient/patientlist.html'
    context_object_name = 'patients'

    def get_queryset(self):
        queryset = Patient.objects.all().order_by('last_name', 'first_name')
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patient/patientupdate.html'
    context_object_name = 'patient'

    def form_valid(self, form):
        messages.success(self.request, "Patient information updated.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Could not update patient. Please check the form.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('patients:patient_detail', kwargs={'pk': self.object.pk})


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
