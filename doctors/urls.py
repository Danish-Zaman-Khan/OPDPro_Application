
from django.urls import path
from . import views

app_name ='doctors'

urlpatterns = [
    path('', views.doctors_list, name='doctors_list'),
    path('<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    
]