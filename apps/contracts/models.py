from django.db import models
from apps.sellers.models import SellerProfile
from apps.products.models import Product


class Contract(models.Model):
    class ContractType(models.TextChoices):
        CONSIGNMENT = 'consignment', 'Consignment Agreement'
        OTHER = 'other', 'Other'

    seller = models.ForeignKey(
        SellerProfile, on_delete=models.PROTECT, related_name='contracts'
    )
    file_url = models.URLField()
    type = models.CharField(max_length=20, choices=ContractType.choices)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.business_name} — {self.type}"

    class Meta:
        ordering = ['-created_at']


class ShippingFeeOption(models.Model):
    class PaidBy(models.TextChoices):
        SELLER = 'seller', 'Seller'
        CUSTOMER = 'customer', 'Customer'

    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name='shipping_fee_option'
    )
    paid_by = models.CharField(max_length=10, choices=PaidBy.choices)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name_en} — paid by {self.paid_by}"