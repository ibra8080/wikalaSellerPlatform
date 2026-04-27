from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import VariantInventory, InboundShipmentUpdate
from .serializers import VariantInventorySerializer, InboundShipmentUpdateSerializer
from apps.sellers.views import IsSeller, IsAdmin
from apps.products.models import Product
from utils.email import send_shipment_updated
import django.utils.timezone as timezone


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

        ownership_transferred_at = None
        if to_status == 'in_warehouse_egypt':
            ownership_transferred_at = timezone.now()

        serializer.save(
            updated_by=self.request.user,
            from_status=product.status,
            ownership_transferred_at=ownership_transferred_at
        )

        product.status = to_status
        product.save()
        send_shipment_updated(product, to_status)


class AdminInventoryDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = VariantInventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = VariantInventory.objects.all()