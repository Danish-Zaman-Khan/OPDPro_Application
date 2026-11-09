from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('', views.appointment_list, name='appointment_list'),
    path('today/', views.today_appointments, name='today_appointments'),
    path('upcoming/', views.upcoming_appointments, name='upcoming_appointments'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('<int:pk>/view/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/viewdetails/', views.appointment_viewdetail, name='appointment_view_detail'),
    path('visit-history/<int:patient_id>/', views.visit_history, name='visit_history'),
    path('<int:pk>/edit-notes/', views.edit_doctor_notes, name='edit_doctor_notes'),
    path('<int:pk>/mark-completed/', views.mark_completed, name='mark_completed'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
]
