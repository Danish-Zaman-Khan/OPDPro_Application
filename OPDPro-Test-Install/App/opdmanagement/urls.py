from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from django.urls import re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('service-worker.js', TemplateView.as_view(template_name='pwa/service-worker.js', content_type='application/javascript'), name='service_worker'),
    path('admin/', admin.site.urls),
    path('', include('usermanagement.urls', namespace='usermanagement')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('appointments/', include('appointment.urls', namespace='appointment')),
    path('doctors/', include('doctors.urls', namespace='doctors')),
    path('notifications/', include('user_notifications.urls', namespace='user_notifications')),
    path('billing/', include('billing.urls', namespace='billing')),
    path('prescriptions/', include('prescriptions.urls', namespace='prescriptions')),
    path('reports/', include('reports.urls', namespace='reports')),
    # API
    path('api/patients/', include('patients.api_urls')),
    path('api/appointments/', include('appointment.api_urls')),
    path('api/usermanagement/', include('usermanagement.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.OPD_LOCAL_DESKTOP:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
else:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
