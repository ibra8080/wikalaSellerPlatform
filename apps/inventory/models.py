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


class ShipmentRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SUBMITTED = 'submitted', 'Submitted'
        ACCEPTED = 'accepted', 'Accepted'
        CANCELLED = 'cancelled', 'Cancelled'

    class DeliveryMethod(models.TextChoices):
        PICKUP = 'pickup', 'Pickup by Wikala'
        COURIER = 'courier', 'Courier'
        DROP_OFF = 'drop_off', 'Drop Off at Wikala'

    seller = models.ForeignKey(
        'sellers.SellerProfile',
        on_delete=models.CASCADE,
        related_name='shipment_requests'
    )
    request_number = models.CharField(max_length=20, unique=True, blank=True)
    requested_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    notes = models.TextField(blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        blank=True
    )
    delivery_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.request_number} — {self.seller.business_name}"

    def save(self, *args, **kwargs):
        if not self.request_number:
            last = ShipmentRequest.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.request_number = f"WKR-{next_num:04d}"
        super().save(*args, **kwargs)


class ShipmentRequestItem(models.Model):
    shipment_request = models.ForeignKey(
        ShipmentRequest,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='shipment_items'
    )
    cartons_count = models.IntegerField()
    units_per_carton = models.IntegerField(default=0)
    total_units = models.IntegerField(default=0)
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

    def save(self, *args, **kwargs):
        if self.product:
            self.units_per_carton = self.product.units_per_carton or 0
            self.carton_weight_kg = self.product.carton_weight_kg
            self.carton_length_cm = self.product.carton_length_cm
            self.carton_width_cm = self.product.carton_width_cm
            self.carton_height_cm = self.product.carton_height_cm
            self.total_units = self.cartons_count * self.units_per_carton
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shipment_request.request_number} — {self.product.name_en}"
