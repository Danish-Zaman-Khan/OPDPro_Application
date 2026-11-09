from django.urls import path
from . import views
app_name = 'billing'
urlpatterns = [
    path('',                          views.billing_dashboard,  name='dashboard'),
    path('invoices/',                 views.invoice_list,       name='invoice_list'),
    path('invoices/new/',             views.create_invoice,     name='create_invoice'),
    path('invoices/new/patient/<int:patient_id>/',         views.create_invoice, name='create_invoice_patient'),
    path('invoices/new/appointment/<int:appointment_id>/', views.create_invoice, name='create_invoice_appt'),
    path('invoices/<int:pk>/',        views.invoice_detail,     name='invoice_detail'),
    path('invoices/<int:pk>/pay/',    views.record_payment,     name='record_payment'),
    path('invoices/<int:pk>/print/',  views.invoice_print,      name='invoice_print'),
    path('settings/',                 views.fee_settings,       name='fee_settings'),
]
