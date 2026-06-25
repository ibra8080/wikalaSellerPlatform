from django.db import models
from apps.sellers.models import SellerProfile


class Category(models.Model):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    name_de = models.CharField(max_length=100, blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='children'
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name_en


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING_REVIEW = 'pending_review', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        AWAITING_SELLER_SHIPMENT = 'awaiting_seller_shipment', 'Awaiting Seller Shipment'
        IN_WAREHOUSE_EGYPT = 'in_warehouse_egypt', 'In Warehouse Egypt'
        IN_TRANSIT = 'in_transit', 'In Transit'
        IN_WAREHOUSE_GERMANY = 'in_warehouse_germany', 'In Warehouse Germany'
        LISTED = 'listed', 'Listed'

    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='products'
    )
    product_code = models.CharField(max_length=20, unique=True, blank=True, null=True, default=None)

    # Names
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    name_de = models.CharField(max_length=200, blank=True)

    # Descriptions
    description_ar = models.TextField()
    description_en = models.TextField(blank=True)
    description_de = models.TextField(blank=True)

    # Marketing descriptions
    marketing_desc_ar = models.TextField(blank=True)
    marketing_desc_en = models.TextField(blank=True)
    marketing_desc_de = models.TextField(blank=True)

    # Product details
    materials = models.TextField(blank=True)
    brand_name = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    custom_specs = models.JSONField(default=list, blank=True)
    keywords = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='products'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    production_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Unit dimensions
    unit_weight_kg = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True
    )
    unit_length_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    unit_width_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    unit_height_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    # Carton dimensions
    units_per_carton = models.IntegerField(null=True, blank=True)
    carton_weight_kg = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True
    )
    carton_length_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    carton_width_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    carton_height_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )

    has_care_label = models.BooleanField(null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT
    )
    rejection_reason = models.TextField(blank=True)
    previous_status = models.CharField(max_length=30, blank=True)
    shopify_product_id = models.CharField(max_length=50, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    listed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_code} — {self.name_en}"

    def save(self, *args, **kwargs):
        if not self.product_code:
            self.product_code = None
        # Generate product_code on approval, using pk for guaranteed uniqueness
        if self.product_code is None and self.status == self.Status.APPROVED:
            if not self.pk:
                super().save(*args, **kwargs)
                args = ()
                kwargs = {}
            seller_num = self.seller.seller_id.replace('WK-', '') if self.seller.seller_id else '0000'
            self.product_code = f"WKP-{seller_num}-{self.pk}"
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images'
    )
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name_en} — image {self.order}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants'
    )
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, default=None)
    external_barcode = models.CharField(
        max_length=50,
        blank=True,
        help_text="EAN-13, UPC, أو أي كود خارجي للبائع"
    )
    quantity_submitted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sku} ({self.color} / {self.size})"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = None
        # Generate readable SKU: {product_code}-{COLOR}-{SIZE}
        if self.sku is None and self.product.product_code:
            if not self.pk:
                super().save(*args, **kwargs)
                args = ()
                kwargs = {}
            color_part = (self.color[:3].upper() if self.color else '').strip()
            size_part = (self.size.upper() if self.size else '').strip()
            suffix_bits = [b for b in [color_part, size_part] if b]
            if suffix_bits:
                suffix = '-'.join(suffix_bits)
            else:
                # No color/size → use pk to stay unique
                suffix = str(self.pk)
            candidate = f"{self.product.product_code}-{suffix}"
            # Guard against collision (same color+size on two variants)
            if ProductVariant.objects.filter(sku=candidate).exclude(pk=self.pk).exists():
                candidate = f"{candidate}-{self.pk}"
            self.sku = candidate
        super().save(*args, **kwargs)


class Certification(models.Model):
    class CertType(models.TextChoices):
        CE = 'CE', 'CE'
        EU_COSMETICS = 'eu_cosmetics', 'EU Cosmetics'
        OTHER = 'other', 'Other'

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='certifications'
    )
    type = models.CharField(max_length=20, choices=CertType.choices)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name_en} — {self.type}"


class ProductPromotion(models.Model):
    class PromoType(models.TextChoices):
        PERCENT = 'discount_percent', 'Discount Percent'
        FIXED = 'discount_fixed', 'Discount Fixed'
        BUNDLE = 'bundle', 'Bundle'

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='promotions'
    )
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='product_promotions'
    )
    promo_type = models.CharField(max_length=20, choices=PromoType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name_en} — {self.promo_type}"