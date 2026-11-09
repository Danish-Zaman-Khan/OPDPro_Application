from django.urls import path
from . import views
app_name = 'reports'
urlpatterns = [
    path('',                              views.report_list,      name='list'),
    path('upload/',                       views.upload_report,    name='upload'),
    path('upload/patient/<int:patient_id>/',          views.upload_report, name='upload_patient'),
    path('upload/appointment/<int:appointment_id>/',  views.upload_report, name='upload_appt'),
    path('<int:pk>/',                     views.report_detail,    name='detail'),
    path('patient/<int:patient_id>/',     views.patient_reports,  name='patient_reports'),
]
