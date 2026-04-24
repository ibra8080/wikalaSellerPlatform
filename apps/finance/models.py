from django.db import models
from apps.sellers.models import SellerProfile
from apps.products.models import Product


class FeeStructure(models.Model):
    seller_registration_fee = models.DecimalField(max_digits=8, decimal_places=2, default=39.99)
    product_listing_fee = models.DecimalField(max_digits=8, decimal_places=2, default=2.00)
    storage_fee_per_cbm = models.DecimalField(max_digits=8, decimal_places=2, default=25.00)
    pick_pack_fee = models.DecimalField(max_digits=8, decimal_places=2, default=1.00)
    commission_wikala = models.DecimalField(max_digits=5, decimal_places=2, default=0.15)
    commission_external = models.DecimalField(max_digits=5, decimal_places=2, default=0.10)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"Fee Structure — {self.effective_from}"


class SellerStatement(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent'
        PAID = 'paid', 'Paid'

    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='statements'
    )
    period_start = models.DateField()
    period_end = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    storage_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pick_pack_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    external_sales_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_end']

    def __str__(self):
        return f"{self.seller.business_name} — {self.period_start} : {self.period_end}"


class SaleRecord(models.Model):
    class Channel(models.TextChoices):
        WIKALA = 'wikala', 'Wikala'
        EXTERNAL = 'external', 'External'

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='sale_records'
    )
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='sale_records'
    )
    statement = models.ForeignKey(
        SellerStatement, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sale_records'
    )
    shopify_order_id = models.CharField(max_length=50, blank=True)
    channel = models.CharField(
        max_length=10,
        choices=Channel.choices,
        default=Channel.WIKALA
    )
    quantity_sold = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.business_name} — {self.product.name_en} — {self.sale_date}"