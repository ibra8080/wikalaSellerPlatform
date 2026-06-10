from django.db import models
from apps.users.models import User


class SellerTier(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return self.name


class SellerProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        SUSPENDED = 'suspended', 'Suspended'

    class ReferralSource(models.TextChoices):
        FACEBOOK = 'facebook', 'Facebook'
        INSTAGRAM = 'instagram', 'Instagram'
        FRIEND = 'friend', 'Friend'
        GROUP = 'group', 'Group'
        OTHER = 'other', 'Other'

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='seller_profile'
    )
    seller_id = models.CharField(max_length=20, unique=True, blank=True)
    full_name = models.CharField(max_length=100)
    business_name = models.CharField(max_length=100, unique=True)
    profile_pic_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)

    # Legal Information
    legal_company_name = models.CharField(max_length=200, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    commercial_register_no = models.CharField(max_length=50, blank=True)
    legal_address = models.TextField(blank=True)

    # Banking Information
    bank_account_holder = models.CharField(max_length=100, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    bank_iban = models.CharField(max_length=50, blank=True)
    bank_swift = models.CharField(max_length=20, blank=True)

    seller_tier = models.ForeignKey(
        SellerTier, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sellers'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    rejection_reason = models.TextField(blank=True)
    exported_before = models.BooleanField(default=False)
    referral_source = models.CharField(
        max_length=20,
        choices=ReferralSource.choices,
        blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} ({self.seller_id})"

    def save(self, *args, **kwargs):
        # FIX: Use self.pk after first save to avoid race condition
        is_new = not self.pk
        if is_new:
            # Save first to get the auto-generated pk
            super().save(*args, **kwargs)
            if not self.seller_id:
                self.seller_id = f"WK-{self.pk:04d}"
                super().save(update_fields=['seller_id'])
        else:
            super().save(*args, **kwargs)


class SellerDocument(models.Model):
    class DocType(models.TextChoices):
        COMMERCIAL_REGISTER = 'commercial_register', 'Commercial Register'
        TAX_CARD = 'tax_card', 'Tax Card'
        OTHER = 'other', 'Other'

    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='documents'
    )
    doc_type = models.CharField(max_length=30, choices=DocType.choices)
    file_url = models.URLField()
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.business_name} — {self.doc_type}"


class Promotion(models.Model):
    class DiscountType(models.TextChoices):
        FEE_WAIVER = 'fee_waiver', 'Fee Waiver'
        DIRECT_DISCOUNT = 'direct_discount', 'Direct Discount'
        COST_COVERAGE = 'cost_coverage', 'Cost Coverage'
        CONDITIONAL = 'conditional', 'Conditional'
        CUSTOM = 'custom', 'Custom'

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    conditions = models.JSONField(default=dict, blank=True)
    target_tier = models.ForeignKey(
        SellerTier, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='promotions'
    )
    max_products = models.IntegerField(null=True, blank=True)
    duration_days = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SellerPromotion(models.Model):
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='promotions'
    )
    promotion = models.ForeignKey(
        Promotion, on_delete=models.CASCADE, related_name='seller_promotions'
    )
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('seller', 'promotion')

    def __str__(self):
        return f"{self.seller.business_name} — {self.promotion.name}"