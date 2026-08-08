from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import ProductVariant
from .models import VariantInventory


@receiver(post_save, sender=ProductVariant)
def create_variant_inventory(sender, instance, created, **kwargs):
    if created:
        VariantInventory.objects.get_or_create(variant=instance)