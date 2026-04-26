from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SellerProfile, SellerDocument, SellerTier
from .serializers import (
    SellerProfileSerializer, SellerRegisterSerializer,
    SellerDocumentSerializer, SellerTierSerializer, SellerPromotionSerializer
)


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'seller'


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'


# Seller registers their profile
class SellerRegisterView(generics.CreateAPIView):
    serializer_class = SellerRegisterSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]


# Seller views/updates their own profile
class SellerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self):
        return self.request.user.seller_profile


# Admin: list all sellers
class SellerListView(generics.ListAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerProfile.objects.all()


# Admin: view/update a specific seller (approve/reject)
class SellerDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerProfile.objects.all()


# Seller: upload documents
class SellerDocumentView(generics.ListCreateAPIView):
    serializer_class = SellerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return self.request.user.seller_profile.documents.all()

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)


# Seller: view their promotions
class SellerPromotionView(generics.ListAPIView):
    serializer_class = SellerPromotionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return self.request.user.seller_profile.promotions.filter(is_active=True)