from django.contrib import admin
from .models import VariantInventory, InboundShipmentUpdate


@admin.register(VariantInventory)
class VariantInventoryAdmin(admin.ModelAdmin):
    list_display = (
        'variant', 'quantity_in_egypt', 'quantity_in_transit',
        'quantity_in_germany', 'quantity_sold', 'updated_at'
    )
    readonly_fields = ('updated_at',)
    search_fields = ('variant__sku',)


@admin.register(InboundShipmentUpdate)
class InboundShipmentUpdateAdmin(admin.ModelAdmin):
    list_display = ('product', 'from_status', 'to_status', 'updated_by', 'created_at')
    list_filter = ('to_status',)
    search_fields = ('product__product_code',)
    readonly_fields = ('created_at',)