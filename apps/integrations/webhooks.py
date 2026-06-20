import json
import hmac
import hashlib
import base64
import logging
from decimal import Decimal
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from apps.products.models import ProductVariant
from apps.finance.models import SaleRecord
from apps.communication.models import Notification
from apps.users.models import User
from .models import UnmatchedSaleRecord

logger = logging.getLogger(__name__)


def _verify_hmac(request_body, hmac_header):
    """Verify the Shopify webhook HMAC signature."""
    secret = getattr(settings, 'SHOPIFY_WEBHOOK_SECRET', '')
    if not secret or not hmac_header:
        return False
    digest = hmac.new(
        secret.encode('utf-8'),
        request_body,
        hashlib.sha256
    ).digest()
    computed = base64.b64encode(digest).decode('utf-8')
    return hmac.compare_digest(computed, hmac_header)


def _notify_admins(title, body, related_url=''):
    """Send a notification to all admin users."""
    admins = User.objects.filter(role='admin')
    notifs = [
        Notification(
            user=admin,
            type='unmatched_sale',
            title=title,
            body=body,
            related_url=related_url,
        )
        for admin in admins
    ]
    if notifs:
        Notification.objects.bulk_create(notifs)


@method_decorator(csrf_exempt, name='dispatch')
class ShopifyOrderWebhook(APIView):
    """Receives Shopify order webhooks.
    CRITICAL: always returns 200 after storing data, so Shopify never
    disables the webhook (which would silently lose all future orders)."""
    permission_classes = [AllowAny]

    def post(self, request):
        raw_body = request.body
        hmac_header = request.headers.get('X-Shopify-Hmac-Sha256', '')

        # 1. Verify the request is genuinely from Shopify
        if not _verify_hmac(raw_body, hmac_header):
            logger.warning("Shopify webhook: HMAC verification failed")
            # 401 here is correct — an unverified request is not from Shopify
            return HttpResponse(status=401)

        # 2. Parse payload (never crash — always return 200 after this point)
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except Exception as e:
            logger.error(f"Shopify webhook: invalid JSON — {e}")
            return HttpResponse(status=200)  # ack so Shopify doesn't retry forever

        try:
            self._process_order(payload)
        except Exception as e:
            # Log but still return 200 — we never want Shopify to disable the webhook
            logger.error(f"Shopify webhook: processing error — {e}", exc_info=True)

        return HttpResponse(status=200)

    def _process_order(self, payload):
        order_id = str(payload.get('id', ''))

        # Parse order date
        created_str = payload.get('created_at', '')
        try:
            sale_date = datetime.fromisoformat(created_str.replace('Z', '+00:00')).date()
        except Exception:
            sale_date = datetime.utcnow().date()

        line_items = payload.get('line_items', [])

        for item in line_items:
            sku = (item.get('sku') or '').strip()
            qty = int(item.get('quantity', 1))
            try:
                unit_price = Decimal(str(item.get('price', '0')))
            except Exception:
                unit_price = Decimal('0')
            total = unit_price * qty
            title = item.get('title', '')

            variant = None
            if sku:
                variant = ProductVariant.objects.filter(sku=sku).select_related('product__seller').first()

            if variant:
                # Duplicate protection: same order + same variant already recorded?
                exists = SaleRecord.objects.filter(
                    shopify_order_id=order_id, variant=variant
                ).exists()
                if exists:
                    continue

                SaleRecord.objects.create(
                    variant=variant,
                    seller=variant.product.seller,
                    shopify_order_id=order_id,
                    channel=SaleRecord.Channel.WIKALA,
                    quantity_sold=qty,
                    unit_price=unit_price,
                    total_amount=total,
                    sale_date=sale_date,
                )
            else:
                # Unmatched — store raw payload, never lose the sale
                already = UnmatchedSaleRecord.objects.filter(
                    shopify_order_id=order_id, raw_sku=sku
                ).exists()
                if already:
                    continue

                UnmatchedSaleRecord.objects.create(
                    shopify_order_id=order_id,
                    raw_sku=sku,
                    line_item_title=title,
                    quantity=qty,
                    unit_price=unit_price,
                    total_amount=total,
                    payload=payload,
                )
                _notify_admins(
                    title="Unmatched Shopify sale",
                    body=f"Order {order_id}: SKU '{sku or '(empty)'}' ({title}) "
                         f"did not match any product variant. Manual review needed.",
                    related_url='/admin/products',
                )