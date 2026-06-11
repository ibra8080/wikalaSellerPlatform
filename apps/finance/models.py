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
        ACCEPTED = 'accepted', 'Accepted'
        DISPUTED = 'disputed', 'Disputed'
        PAID = 'paid', 'Paid'

    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='statements'
    )
    period_start = models.DateField()
    period_end = models.DateField()

    # Cached totals (recalculated from line items)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overall_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_description = models.CharField(max_length=300, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Legacy fields (kept for backward compat)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    storage_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pick_pack_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    external_sales_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.DRAFT
    )
    admin_notes = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    auto_finalize_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end']

    def __str__(self):
        return f"{self.seller.business_name} — {self.period_start} : {self.period_end}"

    def recalculate_totals(self):
        from decimal import Decimal
        sales = Decimal('0')
        fees = Decimal('0')
        for item in self.line_items.all():
            if item.item_type == 'sale':
                sales += item.amount - item.discount
            else:
                fees += item.amount - item.discount
        self.total_sales = sales
        self.total_fees = fees
        self.net_amount = sales - fees - self.overall_discount
        self.save(update_fields=['total_sales', 'total_fees', 'net_amount'])


class StatementLineItem(models.Model):
    class ItemType(models.TextChoices):
        SALE = 'sale', 'Sale'
        VAT = 'vat', 'VAT'
        COMMISSION = 'commission', 'Commission'
        STORAGE = 'storage', 'Storage Fee'
        SHIPPING = 'shipping', 'Shipping Fee'
        PICK_PACK = 'pick_pack', 'Pick & Pack'
        WEB_SERVICE = 'web_service', 'Web Service'
        CUSTOM = 'custom', 'Custom Charge'

    statement = models.ForeignKey(
        SellerStatement, on_delete=models.CASCADE, related_name='line_items'
    )
    item_type = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference_id = models.CharField(max_length=50, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order_index', 'id']

    def __str__(self):
        return f"{self.statement} — {self.description} — €{self.amount}"


class StatementDispute(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        RESOLVED = 'resolved', 'Resolved'
        REJECTED = 'rejected', 'Rejected'

    statement = models.ForeignKey(
        SellerStatement, on_delete=models.CASCADE, related_name='disputes'
    )
    line_item = models.ForeignKey(
        StatementLineItem, on_delete=models.CASCADE,
        null=True, blank=True, related_name='disputes'
    )
    seller_message = models.TextField()
    admin_response = models.TextField(blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Dispute — {self.statement} — {self.status}"


class SaleRecord(models.Model):
    class Channel(models.TextChoices):
        WIKALA = 'wikala', 'Wikala'
        EXTERNAL = 'external', 'External'

    variant = models.ForeignKey(
        'products.ProductVariant', on_delete=models.CASCADE, related_name='sale_records'
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
        return f"{self.seller.business_name} — {self.variant.sku} — {self.sale_date}"

class WebService(models.Model):
    class ServiceType(models.TextChoices):
        ONE_TIME = 'one_time', 'One Time'
        MONTHLY  = 'monthly', 'Monthly'
        EVENT    = 'event', 'Event'

    class ServiceLevel(models.TextChoices):
        SELLER  = 'seller',  'Seller Level'
        PRODUCT = 'product', 'Product Level'

    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type        = models.CharField(max_length=10, choices=ServiceType.choices)
    level       = models.CharField(
        max_length=10,
        choices=ServiceLevel.choices,
        default=ServiceLevel.SELLER
    )
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    mandatory   = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — €{self.price}"


class DiscountCode(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'Percent'
        FIXED   = 'fixed',   'Fixed Amount'

    class AppliesTo(models.TextChoices):
        ALL      = 'all',      'All Services'
        SPECIFIC = 'specific', 'Specific Service'

    code          = models.CharField(max_length=50, unique=True)
    name          = models.CharField(max_length=200)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value         = models.DecimalField(max_digits=8, decimal_places=2)
    applies_to    = models.CharField(max_length=10, choices=AppliesTo.choices, default=AppliesTo.ALL)
    service       = models.ForeignKey(
        WebService, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='discount_codes'
    )
    valid_from    = models.DateField()
    valid_until   = models.DateField(null=True, blank=True)
    max_uses      = models.IntegerField(null=True, blank=True)
    used_count    = models.IntegerField(default=0)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} — {self.name}"

    def is_valid(self):
        from django.utils import timezone
        today = timezone.now().date()
        if not self.is_active:
            return False
        if today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True


class SellerDiscountCode(models.Model):
    """البائع استخدم كود معين"""
    seller     = models.ForeignKey(
        'sellers.SellerProfile', on_delete=models.CASCADE,
        related_name='discount_codes'
    )
    code       = models.ForeignKey(
        DiscountCode, on_delete=models.CASCADE,
        related_name='usages'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seller', 'code')

    def __str__(self):
        return f"{self.seller.business_name} — {self.code.code}"


class SellerDiscount(models.Model):
    """خصم مباشر من الأدمن على بائع معين"""
    class DiscountType(models.TextChoices):
        PERCENT = 'percent', 'Percent'
        FIXED   = 'fixed',   'Fixed Amount'

    seller        = models.ForeignKey(
        'sellers.SellerProfile', on_delete=models.CASCADE,
        related_name='direct_discounts'
    )
    service       = models.ForeignKey(
        WebService, on_delete=models.CASCADE,
        null=True, blank=True, related_name='direct_discounts'
    )
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value         = models.DecimalField(max_digits=8, decimal_places=2)
    valid_until   = models.DateField(null=True, blank=True)
    is_active     = models.BooleanField(default=True)
    note          = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.business_name} — {self.value} {self.discount_type}"


class WebServiceCharge(models.Model):
    """فاتورة خدمة على بائع"""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID    = 'paid',    'Paid'
        WAIVED  = 'waived',  'Waived'

    seller          = models.ForeignKey(
        'sellers.SellerProfile', on_delete=models.CASCADE,
        related_name='service_charges'
    )
    service         = models.ForeignKey(
        WebService, on_delete=models.CASCADE,
        related_name='charges'
    )
    statement       = models.ForeignKey(
        SellerStatement, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='service_charges'
    )
    original_price  = models.DecimalField(max_digits=8, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_price     = models.DecimalField(max_digits=8, decimal_places=2)
    status          = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    product         = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='service_charges'
    )
    period_month    = models.IntegerField(null=True, blank=True)
    period_year     = models.IntegerField(null=True, blank=True)
    notes           = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.business_name} — {self.service.name} — {self.final_price}"