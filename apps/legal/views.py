from rest_framework import generics, permissions
from rest_framework.throttling import AnonRateThrottle
from .models import WiderrufRequest
from .serializers import WiderrufRequestSerializer
from utils.email import (
    send_widerruf_admin_notification,
    send_widerruf_customer_confirmation,
)


class WiderrufThrottle(AnonRateThrottle):
    rate = '10/hour'


class WiderrufCreateView(generics.CreateAPIView):
    """
    Public (guest) endpoint for submitting a Widerruf under § 356a BGB.
    No authentication required — legally mandatory for guest access.

    The two-step flow (form -> confirm screen -> submit) is handled on the
    frontend. This endpoint is hit only on FINAL confirmation, at which point
    we: persist the record (legal timestamp), email the admin, and send the
    customer an automatic Eingangsbestätigung.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [WiderrufThrottle]
    serializer_class = WiderrufRequestSerializer

    def perform_create(self, serializer):
        # Capture evidence-hardening metadata
        ip = self.request.META.get('HTTP_X_FORWARDED_FOR', '')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:1000]

        widerruf = serializer.save(raw_ip=ip or None, user_agent=user_agent)

        # Admin notification (never block the response on email failure)
        send_widerruf_admin_notification(widerruf)

        # Automatic Eingangsbestätigung to the customer
        send_widerruf_customer_confirmation(widerruf)

        if not widerruf.confirmation_sent:
            widerruf.confirmation_sent = True
            widerruf.save(update_fields=['confirmation_sent'])