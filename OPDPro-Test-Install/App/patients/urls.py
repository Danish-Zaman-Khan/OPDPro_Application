from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('register/', views.PatientregisterView.as_view(), name='patient_register'),
    path('<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('', views.PatientListView.as_view(), name='patient_list'),
    path('<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
]
