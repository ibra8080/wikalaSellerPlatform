from django.urls import path
from .webhooks import ShopifyOrderWebhook

urlpatterns = [
    path('shopify/orders/', ShopifyOrderWebhook.as_view(), name='shopify-order-webhook'),
]