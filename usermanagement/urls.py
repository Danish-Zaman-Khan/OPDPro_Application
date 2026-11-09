
from django.urls import path # type: ignore
from . import views

app_name = 'usermanagement'
urlpatterns = [
    path('', views.userlogin, name = 'login'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('dashboard/',views.dashboard, name ='dashboard'),
    path('logout/',views.userlogout,name='logout'),
]
