from rest_framework import serializers
from .models import Contract, ShippingFeeOption


class ContractSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(
        source='seller.business_name', read_only=True
    )

    class Meta:
        model = Contract
        fields = (
            'id', 'seller', 'seller_name', 'file_url',
            'type', 'signed_at', 'created_at'
        )
        read_only_fields = ('id', 'seller_name', 'created_at')


class ShippingFeeOptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name_en', read_only=True
    )

    class Meta:
        model = ShippingFeeOption
        fields = ('id', 'product', 'product_name', 'paid_by', 'notes')
        read_only_fields = ('id',)