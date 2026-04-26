from rest_framework import serializers
from .models import FeeStructure, SellerStatement, SaleRecord


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class SaleRecordSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name_en', read_only=True)

    class Meta:
        model = SaleRecord
        fields = (
            'id', 'product', 'product_name', 'seller',
            'statement', 'shopify_order_id', 'channel',
            'quantity_sold', 'unit_price', 'total_amount',
            'sale_date', 'created_at'
        )
        read_only_fields = ('id', 'seller', 'created_at')


class SellerStatementSerializer(serializers.ModelSerializer):
    sale_records = SaleRecordSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(
        source='seller.business_name', read_only=True
    )

    class Meta:
        model = SellerStatement
        fields = (
            'id', 'seller', 'seller_name', 'period_start', 'period_end',
            'total_sales', 'commission_amount', 'storage_fee_amount',
            'pick_pack_amount', 'shipping_fee_amount', 'external_sales_amount',
            'net_amount', 'status', 'paid_at', 'created_at', 'sale_records'
        )
        read_only_fields = ('id', 'seller', 'created_at')