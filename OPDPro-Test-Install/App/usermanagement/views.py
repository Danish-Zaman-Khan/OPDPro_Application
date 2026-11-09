from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserUpdateProfileForm
from appointment.models import Appointment
from patients.models import Patient
from django.utils import timezone
from datetime import date, timedelta


def mark_missed_appointments():
    now = timezone.now()
    Appointment.objects.filter(date__lt=now.date(), status='Pending').update(status='Missed')
    Appointment.objects.filter(date=now.date(), time__lt=now.time(), status='Pending').update(status='Missed')


def userlogin(request):
    if request.user.is_authenticated:
        return redirect('usermanagement:dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('usermanagement:dashboard')
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        else:
            messages.error(request, 'Invalid login credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'usermanagement/login.html', {'form': form})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('usermanagement:update_profile')
    else:
        form = UserUpdateProfileForm(instance=request.user)
    return render(request, 'usermanagement/updateprofile.html', {'form': form})


@login_required
def dashboard(request):
    mark_missed_appointments()
    today = date.today()
    seven_days_later = today + timedelta(days=7)

    todays_appointments = Appointment.objects.filter(
        doctor=request.user, date=today
    ).exclude(status='Completed').order_by('time')

    upcoming_appointments = Appointment.objects.filter(
        doctor=request.user,
        date__gt=today,
        date__lte=seven_days_later,
    ).exclude(status='Completed').order_by('date', 'time')

    total_user_appointments = Appointment.objects.filter(doctor=request.user).count()
    completed_today = Appointment.objects.filter(doctor=request.user, date=today, status='Completed').count()
    pending_count = Appointment.objects.filter(doctor=request.user, status='Pending').count()

    context = {
        'current_day': today,
        'total_patients': Patient.objects.count(),
        'total_appointments': total_user_appointments,
        'todays_appointments': todays_appointments,
        'upcoming_appointments': upcoming_appointments,
        'completed_today': completed_today,
        'pending_count': pending_count,
    }
    return render(request, 'usermanagement/userdashboard.html', context)


def userlogout(request):
    logout(request)
    return redirect('usermanagement:login')


# API views
from rest_framework import viewsets
from .models import CustomUser
from .serializers import CustomUserSerializer
from rest_framework.permissions import IsAuthenticated

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers as drf_serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        user = authenticate(email=attrs.get('email'), password=attrs.get('password'))
        if user is None:
            raise drf_serializers.ValidationError('Invalid credentials')
        data = super().validate({'username': user.username, 'password': attrs.get('password')})
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
