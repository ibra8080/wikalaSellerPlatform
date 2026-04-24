from django.db import models
from apps.products.models import Product, ProductVariant
from apps.users.models import User


class VariantInventory(models.Model):
    variant = models.OneToOneField(
        ProductVariant, on_delete=models.CASCADE, related_name='inventory'
    )
    quantity_in_egypt = models.IntegerField(default=0)
    quantity_in_transit = models.IntegerField(default=0)
    quantity_in_germany = models.IntegerField(default=0)
    quantity_sold = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Variant Inventories'

    @property
    def quantity_available(self):
        return self.quantity_in_germany - self.quantity_sold

    def __str__(self):
        return f"Inventory — {self.variant.sku}"


class InboundShipmentUpdate(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='shipment_updates'
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    ownership_transferred_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_code}: {self.from_status} → {self.to_status}"