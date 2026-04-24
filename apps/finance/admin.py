from django.contrib import admin
from .models import FeeStructure, SellerStatement, SaleRecord


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        'effective_from', 'seller_registration_fee', 'product_listing_fee',
        'storage_fee_per_cbm', 'commission_wikala', 'is_active'
    )
    list_filter = ('is_active',)


@admin.register(SellerStatement)
class SellerStatementAdmin(admin.ModelAdmin):
    list_display = (
        'seller', 'period_start', 'period_end',
        'total_sales', 'net_amount', 'status', 'paid_at'
    )
    list_filter = ('status',)
    search_fields = ('seller__business_name',)
    readonly_fields = ('created_at',)


@admin.register(SaleRecord)
class SaleRecordAdmin(admin.ModelAdmin):
    list_display = (
        'seller', 'product', 'channel',
        'quantity_sold', 'total_amount', 'sale_date'
    )
    list_filter = ('channel',)
    search_fields = ('seller__business_name', 'product__name_en', 'shopify_order_id')