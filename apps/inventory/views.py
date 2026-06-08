from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import VariantInventory, InboundShipmentUpdate, ShipmentRequest
from .serializers import VariantInventorySerializer, InboundShipmentUpdateSerializer, ShipmentRequestSerializer
from apps.sellers.views import IsSeller, IsAdmin
from apps.products.models import Product
from utils.email import send_shipment_updated
import django.utils.timezone as timezone


# Valid status transitions for shipments
VALID_STATUS_TRANSITIONS = {
    'approved': ['awaiting_seller_shipment'],
    'awaiting_seller_shipment': ['in_warehouse_egypt'],
    'in_warehouse_egypt': ['in_transit'],
    'in_transit': ['in_warehouse_germany'],
    'in_warehouse_germany': ['listed'],
}


class SellerInventoryView(generics.ListAPIView):
    serializer_class = VariantInventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return VariantInventory.objects.filter(
            variant__product__seller=self.request.user.seller_profile
        )


class ShipmentUpdateListView(generics.ListAPIView):
    serializer_class = InboundShipmentUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return InboundShipmentUpdate.objects.filter(
            product__seller=self.request.user.seller_profile
        ).order_by('-created_at')


class AdminShipmentUpdateView(generics.CreateAPIView):
    serializer_class = InboundShipmentUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        to_status = serializer.validated_data['to_status']
        current_status = product.status

        # Validate status transition
        allowed = VALID_STATUS_TRANSITIONS.get(current_status, [])
        if to_status not in allowed:
            raise ValidationError({
                'to_status': (
                    f"Cannot transition from '{current_status}' to '{to_status}'. "
                    f"Allowed transitions: {allowed or 'none'}"
                )
            })

        ownership_transferred_at = None
        if to_status == 'in_warehouse_egypt':
            ownership_transferred_at = timezone.now()

        serializer.save(
            updated_by=self.request.user,
            from_status=current_status,
            ownership_transferred_at=ownership_transferred_at
        )

        product.status = to_status
        product.save()
        send_shipment_updated(product, to_status)


class AdminInventoryDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = VariantInventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = VariantInventory.objects.all()


# ── Seller: Shipment Requests ──

class ShipmentRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ShipmentRequest.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-created_at')


class ShipmentRequestDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ShipmentRequest.objects.filter(
            seller=self.request.user.seller_profile
        )

    def perform_destroy(self, instance):
        if instance.status not in ('draft', 'cancelled'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Only draft or cancelled requests can be deleted.')
        instance.delete()


# ── Admin: Shipment Requests ──

class AdminShipmentRequestListView(generics.ListAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = ShipmentRequest.objects.all().order_by('-created_at')


class AdminShipmentRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = ShipmentRequest.objects.all()