from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import VariantInventory, InboundShipmentUpdate, ShipmentRequest, ShipmentRequestItem
from .serializers import VariantInventorySerializer, InboundShipmentUpdateSerializer, ShipmentRequestSerializer, ShipmentRequestItemSerializer
from utils.email import send_shipment_request_accepted, send_shipment_updated
from apps.sellers.views import IsSeller, IsAdmin
from apps.products.models import Product
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

        if to_status == 'in_warehouse_germany':
            from apps.inventory.models import VariantInventory
            for variant in product.variants.all():
                inv, created = VariantInventory.objects.get_or_create(variant=variant)
                inv.arrived_germany_at = timezone.now()
                inv.save()

        send_shipment_updated(product, to_status)


class AdminInventoryDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = VariantInventorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = VariantInventory.objects.all()


class ShipmentRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ShipmentRequest.objects.filter(
            seller=self.request.user.seller_profile
        ).order_by('-created_at')


class ShipmentRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        return ShipmentRequest.objects.filter(
            seller=self.request.user.seller_profile
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.status in ['accepted']:
            raise permissions.PermissionDenied(
                'Cannot modify an accepted shipment request.'
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.status in ['accepted']:
            raise permissions.PermissionDenied(
                'Cannot delete an accepted shipment request.'
            )
        instance.delete()


class AdminShipmentRequestListView(generics.ListAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = ShipmentRequest.objects.all().order_by('-created_at')


class AdminShipmentRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ShipmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = ShipmentRequest.objects.all()

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = self.request.data.get('status')

        if new_status == 'accepted':
            serializer.save()
            try:
                send_shipment_request_accepted(instance)
            except Exception:
                pass
        else:
            serializer.save()