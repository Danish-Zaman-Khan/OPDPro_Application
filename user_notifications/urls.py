from django.urls import path
from . import views

app_name = 'user_notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('send/to/<int:recipient_pk>/', views.send_message, name='send_message'),
    path('send/reply/<int:notification_pk>/', views.send_message, name='reply_message'),
    path('mark-read/<int:pk>/', views.mark_as_read, name='mark_as_read'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
]
