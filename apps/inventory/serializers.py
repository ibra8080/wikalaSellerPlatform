from rest_framework import serializers
from .models import VariantInventory, InboundShipmentUpdate


class VariantInventorySerializer(serializers.ModelSerializer):
    quantity_available = serializers.ReadOnlyField()
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)

    class Meta:
        model = VariantInventory
        fields = (
            'id', 'variant', 'variant_sku',
            'quantity_in_egypt', 'quantity_in_transit',
            'quantity_in_germany', 'quantity_sold',
            'quantity_available', 'updated_at'
        )
        read_only_fields = ('id', 'variant', 'variant_sku', 'updated_at')


class InboundShipmentUpdateSerializer(serializers.ModelSerializer):
    updated_by_email = serializers.CharField(
        source='updated_by.email', read_only=True
    )

    class Meta:
        model = InboundShipmentUpdate
        fields = (
            'id', 'product', 'updated_by', 'updated_by_email',
            'from_status', 'to_status',
            'ownership_transferred_at', 'note', 'created_at'
        )
        read_only_fields = ('id', 'updated_by', 'updated_by_email', 'created_at')