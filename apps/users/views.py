import os
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    FullRegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)
from .models import User
from apps.sellers.models import SellerProfile
from utils.email import send_password_reset


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'


class ValidateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        errors = {}
        email = request.data.get('email', '')
        username = request.data.get('username', '')

        if email and User.objects.filter(email=email).exists():
            errors['email'] = ['This email is already registered.']
        if username and User.objects.filter(username=username).exists():
            errors['username'] = ['This username is already taken.']

        business_name = request.data.get('business_name', '')

        if business_name and SellerProfile.objects.filter(business_name=business_name).exists():
            errors['business_name'] = ['This business name is already taken.']

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'valid': True})


class FullRegisterView(generics.CreateAPIView):
    serializer_class = FullRegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            frontend = os.getenv('FRONTEND_URL', 'https://sellers.wikala.net')
            reset_url = f'{frontend}/reset-password?uid={uid}&token={token}'
            send_password_reset(user, reset_url)
        except User.DoesNotExist:
            pass

        return Response(
            {'detail': 'If an account exists for this email, a reset link has been sent.'}
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'detail': 'Password has been reset successfully.'})


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({'detail': 'Password changed successfully.'})