from django.contrib import admin
from .models import UnmatchedSaleRecord


@admin.register(UnmatchedSaleRecord)
class UnmatchedSaleRecordAdmin(admin.ModelAdmin):
    list_display = ('shopify_order_id', 'raw_sku', 'line_item_title',
                    'quantity', 'total_amount', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('shopify_order_id', 'raw_sku', 'line_item_title')
    readonly_fields = ('shopify_order_id', 'raw_sku', 'line_item_title',
                       'quantity', 'unit_price', 'total_amount', 'payload', 'created_at')