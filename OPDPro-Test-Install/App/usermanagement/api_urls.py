from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomUserViewSet, CustomTokenObtainPairSerializer, CustomTokenObtainPairView

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='customuser')

urlpatterns = [
    path('', include(router.urls)),  # Your existing /users/ endpoint
   # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  #Login endpoint
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  #Token refresh
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

]
