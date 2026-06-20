from django.db import models


class UnmatchedSaleRecord(models.Model):
    """Stores Shopify orders whose SKU did not match any ProductVariant.
    The raw payload is preserved so the sale can be reconciled manually —
    the money was received even if matching failed."""
    shopify_order_id = models.CharField(max_length=50, db_index=True)
    raw_sku = models.CharField(max_length=100, blank=True)
    line_item_title = models.CharField(max_length=255, blank=True)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payload = models.JSONField(help_text="Full raw Shopify order payload")
    is_resolved = models.BooleanField(default=False)
    resolved_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Unmatched: {self.raw_sku} (order {self.shopify_order_id})"
