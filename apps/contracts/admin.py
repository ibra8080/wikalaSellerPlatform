from django.contrib import admin
from .models import Contract, ShippingFeeOption


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('seller', 'type', 'signed_at', 'created_at')
    list_filter = ('type',)
    search_fields = ('seller__business_name',)
    readonly_fields = ('created_at',)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ShippingFeeOption)
class ShippingFeeOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'paid_by')
    list_filter = ('paid_by',)