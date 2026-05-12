from rest_framework import serializers
from .models import VariantInventory, InboundShipmentUpdate, ShipmentRequest, ShipmentRequestItem


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
        read_only_fields = (
            'id', 'updated_by', 'updated_by_email',
            'from_status', 'created_at'
        )


class ShipmentRequestItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_en', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)

    class Meta:
        model = ShipmentRequestItem
        fields = (
            'id', 'product', 'product_name', 'product_code',
            'cartons_count', 'units_per_carton', 'total_units',
            'carton_weight_kg', 'carton_length_cm',
            'carton_width_cm', 'carton_height_cm',
        )
        read_only_fields = (
            'units_per_carton', 'total_units',
            'carton_weight_kg', 'carton_length_cm',
            'carton_width_cm', 'carton_height_cm',
        )


class ShipmentRequestSerializer(serializers.ModelSerializer):
    items = ShipmentRequestItemSerializer(many=True, required=False)
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)

    class Meta:
        model = ShipmentRequest
        fields = (
            'id', 'request_number', 'seller', 'seller_name',
            'requested_date', 'status', 'notes',
            'delivery_date', 'delivery_method', 'delivery_notes',
            'created_at', 'updated_at', 'items',
        )
        read_only_fields = (
            'id', 'request_number', 'seller', 'seller_name',
            'delivery_date', 'delivery_method', 'delivery_notes',
            'created_at', 'updated_at',
        )

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        seller = self.context['request'].user.seller_profile
        shipment = ShipmentRequest.objects.create(seller=seller, **validated_data)
        for item in items_data:
            ShipmentRequestItem.objects.create(shipment_request=shipment, **item)
        return shipment