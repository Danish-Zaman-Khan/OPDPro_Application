from django.urls import path
from . import views
app_name = 'prescriptions'
urlpatterns = [
    path('',                         views.prescription_list,   name='list'),
    path('new/',                     views.create_prescription,  name='create'),
    path('new/patient/<int:patient_id>/',         views.create_prescription, name='create_patient'),
    path('new/appointment/<int:appointment_id>/', views.create_prescription, name='create_appt'),
    path('<int:pk>/',                views.prescription_detail,  name='detail'),
    path('<int:pk>/print/',          views.prescription_print,   name='print'),
    path('<int:pk>/dispense/',       views.dispense_prescription,name='dispense'),
    path('api/drugs/',               views.drug_search_api,      name='drug_search'),
]
