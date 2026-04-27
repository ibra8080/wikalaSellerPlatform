from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import SellerProfile, SellerDocument, SellerTier
from .serializers import (
    SellerProfileSerializer, SellerRegisterSerializer,
    SellerDocumentSerializer, SellerTierSerializer, SellerPromotionSerializer
)
from utils.cloudinary import upload_document
from utils.email import send_seller_approved, send_seller_rejected


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

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'approved' and not instance.approved_at:
            instance.approved_at = timezone.now()
            instance.save()
            send_seller_approved(instance)
        elif instance.status == 'rejected':
            send_seller_rejected(instance)


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


class SellerDocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        doc_type = request.data.get('doc_type')

        if not file or not doc_type:
            return Response(
                {'error': 'file and doc_type are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        url = upload_document(file, folder='seller_documents')
        document = SellerDocument.objects.create(
            seller=request.user.seller_profile,
            doc_type=doc_type,
            file_url=url
        )
        return Response(
            SellerDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )