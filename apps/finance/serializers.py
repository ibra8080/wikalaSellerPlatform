from rest_framework import serializers
from .models import (
    FeeStructure, SellerStatement, SaleRecord,
    WebService, DiscountCode, SellerDiscountCode,
    SellerDiscount, WebServiceCharge
)

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
        read_only_fields = ('id', 'seller_name', 'created_at')

class WebServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebService
        fields = (
            'id', 'name', 'description', 'type',
            'price', 'mandatory', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class DiscountCodeSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    is_valid     = serializers.SerializerMethodField()

    class Meta:
        model = DiscountCode
        fields = (
            'id', 'code', 'name', 'discount_type', 'value',
            'applies_to', 'service', 'service_name',
            'valid_from', 'valid_until', 'max_uses', 'used_count',
            'is_active', 'is_valid', 'created_at'
        )
        read_only_fields = ('id', 'used_count', 'created_at')

    def get_is_valid(self, obj):
        return obj.is_valid()


class SellerDiscountCodeSerializer(serializers.ModelSerializer):
    code_detail = DiscountCodeSerializer(source='code', read_only=True)

    class Meta:
        model = SellerDiscountCode
        fields = ('id', 'seller', 'code', 'code_detail', 'applied_at')
        read_only_fields = ('id', 'seller', 'applied_at')


class SellerDiscountSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    seller_name  = serializers.CharField(source='seller.business_name', read_only=True)

    class Meta:
        model = SellerDiscount
        fields = (
            'id', 'seller', 'seller_name', 'service', 'service_name',
            'discount_type', 'value', 'valid_until',
            'is_active', 'note', 'created_at'
        )
        read_only_fields = ('id', 'seller_name', 'service_name', 'created_at')


class WebServiceChargeSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    seller_name  = serializers.CharField(source='seller.business_name', read_only=True)

    class Meta:
        model = WebServiceCharge
        fields = (
            'id', 'seller', 'seller_name', 'service', 'service_name',
            'statement', 'original_price', 'discount_amount', 'final_price',
            'status', 'period_month', 'period_year', 'notes', 'created_at'
        )
        read_only_fields = ('id', 'seller_name', 'service_name', 'created_at')