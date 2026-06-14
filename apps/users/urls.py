from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.users.views import RegisterView, ValidateUserView, MeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('validate/', ValidateUserView.as_view(), name='user-validate'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]