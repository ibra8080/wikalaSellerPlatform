from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.views import RegisterView, ValidateUserView, FullRegisterView, MeView, ThrottledTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register-full/', FullRegisterView.as_view(), name='register-full'),
    path('validate/', ValidateUserView.as_view(), name='user-validate'),
    path('login/', ThrottledTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]