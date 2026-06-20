from django.db import models
from apps.users.models import User
from apps.sellers.models import SellerProfile
from apps.products.models import Product


class Conversation(models.Model):
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='conversations'
    )
    subject = models.CharField(max_length=200)
    related_product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.business_name} — {self.subject}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.email} — {self.created_at:%Y-%m-%d %H:%M}"


class Issue(models.Model):
    class Category(models.TextChoices):
        SHIPPING = 'shipping', 'Shipping'
        PAYMENT = 'payment', 'Payment'
        PRODUCT = 'product', 'Product'
        OTHER = 'other', 'Other'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    issue_number = models.CharField(max_length=20, unique=True, blank=True)
    seller = models.ForeignKey(
        SellerProfile, on_delete=models.CASCADE, related_name='issues'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN
    )
    related_product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='issues'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.issue_number} — {self.title}"

    def save(self, *args, **kwargs):
        # FIX: Use self.pk after first save to avoid race condition
        is_new = not self.pk
        if is_new:
            super().save(*args, **kwargs)
            if not self.issue_number:
                self.issue_number = f"WK-ISS-{self.pk:04d}"
                super().save(update_fields=['issue_number'])
        else:
            super().save(*args, **kwargs)


class IssueMessage(models.Model):
    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='issue_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.issue.issue_number} — {self.sender.email}"


class Notification(models.Model):
    class NotifType(models.TextChoices):
        PRODUCT_APPROVED = 'product_approved', 'Product Approved'
        PRODUCT_REJECTED = 'product_rejected', 'Product Rejected'
        SHIPMENT_UPDATED = 'shipment_updated', 'Shipment Updated'
        MESSAGE_RECEIVED = 'message_received', 'Message Received'
        ISSUE_UPDATED = 'issue_updated', 'Issue Updated'
        STATEMENT_READY = 'statement_ready', 'Statement Ready'
        SELLER_APPROVED = 'seller_approved', 'Seller Approved'
        SELLER_REJECTED = 'seller_rejected', 'Seller Rejected'
        UNMATCHED_SALE = 'unmatched_sale', 'Unmatched Sale'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=NotifType.choices)
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    related_url = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} — {self.type}"