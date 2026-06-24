"""
Generate / clear test SaleRecords on any environment.
All test records use shopify_order_id starting with 'TEST-' for safe cleanup.

Usage:
    python manage.py seed_test_sales          # create test data
    python manage.py seed_test_sales --clear  # delete all TEST- records
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from apps.products.models import ProductVariant
from apps.finance.models import SaleRecord


class Command(BaseCommand):
    help = 'Seed or clear test sale records'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete all TEST- records')

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = SaleRecord.objects.filter(shopify_order_id__startswith='TEST-').delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} test sale records'))
            return

        variants = list(
            ProductVariant.objects.exclude(sku='').exclude(sku__isnull=True)
            .select_related('product__seller')
        )
        if not variants:
            self.stdout.write(self.style.ERROR('No variants with SKU found. Aborting.'))
            return

        today = date.today()
        created = 0
        for days_ago in range(0, 365):
            n_sales = random.choices([0, 1, 2, 3], weights=[50, 30, 15, 5])[0]
            sale_day = today - timedelta(days=days_ago)
            for _ in range(n_sales):
                v = random.choice(variants)
                qty = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
                unit_price = v.product.price
                SaleRecord.objects.create(
                    variant=v,
                    seller=v.product.seller,
                    shopify_order_id=f"TEST-{days_ago}-{random.randint(1000,9999)}",
                    channel='wikala',
                    quantity_sold=qty,
                    unit_price=unit_price,
                    total_amount=unit_price * qty,
                    sale_date=sale_day,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {created} test sale records. Total now: {SaleRecord.objects.count()}'
        ))