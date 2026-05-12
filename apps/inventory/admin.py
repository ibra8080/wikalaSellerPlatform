from django.contrib import admin
from .models import VariantInventory, InboundShipmentUpdate, ShipmentRequest, ShipmentRequestItem


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


class ShipmentRequestItemInline(admin.TabularInline):
    model = ShipmentRequestItem
    extra = 0
    readonly_fields = ('units_per_carton', 'total_units', 'carton_weight_kg',
                       'carton_length_cm', 'carton_width_cm', 'carton_height_cm')


@admin.register(ShipmentRequest)
class ShipmentRequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'seller', 'status', 'requested_date',
                    'delivery_date', 'delivery_method', 'created_at')
    list_filter = ('status', 'delivery_method')
    search_fields = ('request_number', 'seller__business_name')
    readonly_fields = ('request_number', 'created_at', 'updated_at')
    inlines = [ShipmentRequestItemInline]