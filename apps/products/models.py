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
    product_code = models.CharField(max_length=20, unique=True, blank=True)

    # Names
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    name_de = models.CharField(max_length=200, blank=True)

    # Descriptions
    description_ar = models.TextField()
    description_en = models.TextField()
    description_de = models.TextField(blank=True)

    # Marketing descriptions
    marketing_desc_ar = models.TextField(blank=True)
    marketing_desc_en = models.TextField(blank=True)
    marketing_desc_de = models.TextField(blank=True)

    # Product details
    materials = models.TextField(blank=True)
    brand_name = models.CharField(max_length=100, blank=True)
    keywords = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='products'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

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
    shopify_product_id = models.CharField(max_length=50, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    listed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_code} — {self.name_en}"

    def save(self, *args, **kwargs):
        if not self.product_code and self.status == self.Status.APPROVED:
            last = Product.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.product_code = f"WKP-{next_id:05d}"
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
    sku = models.CharField(max_length=50, unique=True, blank=True)
    quantity_submitted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sku} ({self.color} / {self.size})"

    def save(self, *args, **kwargs):
        if not self.sku:
            parts = [self.product.product_code]
            if self.color:
                parts.append(self.color[:3].upper())
            if self.size:
                parts.append(self.size.upper())
            self.sku = "-".join(parts)
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