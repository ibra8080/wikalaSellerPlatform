from rest_framework import serializers
from .models import (
    FeeStructure, SellerStatement, SaleRecord,
    WebService, DiscountCode, SellerDiscountCode,
    SellerDiscount, WebServiceCharge,
    StatementLineItem, StatementDispute
)

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class SaleRecordSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(source='variant.sku', read_only=True)

    class Meta:
        model = SaleRecord
        fields = (
            'id', 'variant', 'variant_sku', 'seller',
            'statement', 'shopify_order_id', 'channel',
            'quantity_sold', 'unit_price', 'total_amount',
            'sale_date', 'created_at'
        )
        read_only_fields = ('id', 'seller', 'created_at')


class StatementLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementLineItem
        fields = (
            'id', 'item_type', 'description', 'quantity',
            'unit_price', 'amount', 'discount', 'reference_id', 'order_index'
        )


class StatementDisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatementDispute
        fields = (
            'id', 'line_item', 'seller_message', 'admin_response',
            'status', 'created_at', 'resolved_at'
        )
        read_only_fields = ('id', 'admin_response', 'status', 'created_at', 'resolved_at')


class SellerStatementSerializer(serializers.ModelSerializer):
    line_items = StatementLineItemSerializer(many=True, read_only=True)
    disputes = StatementDisputeSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    has_dispute = serializers.SerializerMethodField()

    class Meta:
        model = SellerStatement
        fields = (
            'id', 'seller', 'seller_name', 'period_start', 'period_end',
            'total_sales', 'total_fees', 'overall_discount', 'net_amount',
            'commission_amount', 'storage_fee_amount', 'pick_pack_amount',
            'shipping_fee_amount', 'external_sales_amount',
            'status', 'admin_notes', 'sent_at', 'auto_finalize_date',
            'paid_at', 'created_at', 'updated_at',
            'line_items', 'disputes', 'has_dispute'
        )
        read_only_fields = ('id', 'seller_name', 'created_at', 'updated_at', 'has_dispute')

    def get_has_dispute(self, obj):
        return obj.disputes.filter(status='open').exists()

class WebServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebService
        fields = (
            'id', 'name', 'description', 'type', 'level',
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
    service_name  = serializers.CharField(source='service.name', read_only=True)
    service_level = serializers.CharField(source='service.level', read_only=True)
    seller_name   = serializers.CharField(source='seller.business_name', read_only=True)
    product_name  = serializers.CharField(source='product.name_en', read_only=True, allow_null=True)

    class Meta:
        model = WebServiceCharge
        fields = (
            'id', 'seller', 'seller_name', 'service', 'service_name', 'service_level',
            'product', 'product_name',
            'statement', 'original_price', 'discount_amount', 'final_price',
            'status', 'period_month', 'period_year', 'notes', 'created_at'
        )
        read_only_fields = ('id', 'seller_name', 'service_name', 'service_level', 'product_name', 'created_at')