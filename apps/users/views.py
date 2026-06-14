from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, UserSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ValidateUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        errors = {}
        email = request.data.get('email', '')
        username = request.data.get('username', '')

        if email and User.objects.filter(email=email).exists():
            errors['email'] = 'This email is already registered.'
        if username and User.objects.filter(username=username).exists():
            errors['username'] = 'This username is already taken.'

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'valid': True})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user