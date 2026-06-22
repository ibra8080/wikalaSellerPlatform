"""Temporary script to generate test SaleRecords. DELETE after testing."""
import os, django, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from apps.products.models import ProductVariant
from apps.finance.models import SaleRecord

variants = list(ProductVariant.objects.exclude(sku='').exclude(sku__isnull=True).select_related('product__seller'))
if not variants:
    print("No variants with SKU found. Aborting.")
    exit()

print(f"Found {len(variants)} variants. Generating test sales...")

today = date.today()
created = 0

# Spread sales across the last 12 months
for days_ago in range(0, 365):
    # Random chance of sales on any given day (more recent = more likely)
    n_sales = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
    sale_day = today - timedelta(days=days_ago)
    for _ in range(n_sales):
        v = random.choice(variants)
        qty = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
        unit_price = v.product.price
        total = unit_price * qty
        SaleRecord.objects.create(
            variant=v,
            seller=v.product.seller,
            shopify_order_id=f"TEST-{days_ago}-{random.randint(1000,9999)}",
            channel='wikala',
            quantity_sold=qty,
            unit_price=unit_price,
            total_amount=total,
            sale_date=sale_day,
        )
        created += 1

print(f"✅ Created {created} test SaleRecords across 12 months")
print(f"Total SaleRecords now: {SaleRecord.objects.count()}")