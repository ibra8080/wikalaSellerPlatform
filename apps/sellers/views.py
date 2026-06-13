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
import logging
logger = logging.getLogger(__name__)


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'seller' and hasattr(request.user, 'seller_profile')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_superuser


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
class SellerDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = SellerProfile.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'approved' and not instance.approved_at:
            instance.approved_at = timezone.now()
            instance.save()
            send_seller_approved(instance)
            # Auto-create registration charge
            self._create_registration_charge(instance)
        elif instance.status == 'rejected':
            send_seller_rejected(instance)

    def _create_registration_charge(self, seller):
        from apps.finance.models import (
            WebService, WebServiceCharge, SellerDiscount, SellerDiscountCode
        )
        from decimal import Decimal
        try:
            service = WebService.objects.filter(
                type='one_time', mandatory=True, is_active=True
            ).first()
            if not service:
                return
            if WebServiceCharge.objects.filter(seller=seller, service=service).exists():
                return
            original_price = service.price
            discount_amount = Decimal('0')
            # Direct discount
            direct = SellerDiscount.objects.filter(
                seller=seller, service=service, is_active=True
            ).first()
            if direct:
                if direct.discount_type == 'percent':
                    discount_amount = original_price * direct.value / 100
                else:
                    discount_amount = direct.value
            # Code discount
            code_usage = SellerDiscountCode.objects.filter(
                seller=seller, code__is_active=True
            ).select_related('code').first()
            if code_usage and code_usage.code.is_valid():
                code = code_usage.code
                if code.applies_to == 'all' or code.service == service:
                    if code.discount_type == 'percent':
                        code_disc = original_price * code.value / 100
                    else:
                        code_disc = code.value
                    discount_amount = max(discount_amount, code_disc)
            final_price = max(Decimal('0'), original_price - discount_amount)
            WebServiceCharge.objects.create(
                seller=seller,
                service=service,
                original_price=original_price,
                discount_amount=discount_amount,
                final_price=final_price,
                status='waived' if final_price == 0 else 'pending',
            )
        except Exception as e:
            logger.error(f"Registration charge error: {e}")


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