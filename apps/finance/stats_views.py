"""
Sales statistics & filtered sales lists.
Read-only aggregations for dashboard cards, charts, and the detailed sales page.
Used by both seller (own data) and admin (all data).
"""
from datetime import date, timedelta

from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDay
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import SaleRecord, SellerStatement
from .serializers import SaleRecordSerializer
from apps.sellers.views import IsSeller, IsAdmin


# ──────────────────────────────────────
# Helpers
# ──────────────────────────────────────

def _aggregate(qs):
    """Total orders (rows), units, and revenue for a queryset."""
    agg = qs.aggregate(
        orders=Count('id'),
        units=Sum('quantity_sold'),
        revenue=Sum('total_amount'),
    )
    return {
        'orders': agg['orders'] or 0,
        'units': agg['units'] or 0,
        'revenue': float(agg['revenue'] or 0),
    }


def _monthly_series(qs, months=12):
    """Revenue + order count grouped by month, last `months` months."""
    start = (date.today().replace(day=1) - timedelta(days=365))
    rows = (
        qs.filter(sale_date__gte=start)
        .annotate(m=TruncMonth('sale_date'))
        .values('m')
        .annotate(orders=Count('id'), revenue=Sum('total_amount'))
        .order_by('m')
    )
    return [
        {
            'month': r['m'].strftime('%Y-%m'),
            'orders': r['orders'],
            'revenue': float(r['revenue'] or 0),
        }
        for r in rows
    ]


def _daily_series(qs):
    """Revenue + order count per day for the current month."""
    today = date.today()
    start = today.replace(day=1)
    rows = (
        qs.filter(sale_date__gte=start, sale_date__lte=today)
        .annotate(d=TruncDay('sale_date'))
        .values('d')
        .annotate(orders=Count('id'), revenue=Sum('total_amount'))
        .order_by('d')
    )
    return [
        {
            'day': r['d'].strftime('%Y-%m-%d'),
            'orders': r['orders'],
            'revenue': float(r['revenue'] or 0),
        }
        for r in rows
    ]


def _build_stats(qs, include_per_seller=False):
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    stats = {
        'today': _aggregate(qs.filter(sale_date=today)),
        'month': _aggregate(qs.filter(sale_date__gte=month_start)),
        'year': _aggregate(qs.filter(sale_date__gte=year_start)),
        'all_time': _aggregate(qs),
        'monthly_chart': _monthly_series(qs),
        'daily_chart': _daily_series(qs),
    }

    if include_per_seller:
        per_seller = (
            qs.values('seller', 'seller__business_name')
            .annotate(orders=Count('id'), revenue=Sum('total_amount'))
            .order_by('-revenue')
        )
        stats['per_seller'] = [
            {
                'seller_id': r['seller'],
                'seller_name': r['seller__business_name'],
                'orders': r['orders'],
                'revenue': float(r['revenue'] or 0),
            }
            for r in per_seller
        ]

    return stats


def _sellers_payout(year=None):
    """Yearly payout totals: paid (status=paid) vs pending (sent + accepted)."""
    if year is None:
        year = date.today().year
    qs = SellerStatement.objects.filter(period_end__year=year)
    paid = qs.filter(status='paid').aggregate(t=Sum('net_amount'))['t'] or 0
    pending = qs.filter(status__in=['sent', 'accepted']).aggregate(t=Sum('net_amount'))['t'] or 0
    return {'paid': float(paid), 'pending': float(pending)}


# ──────────────────────────────────────
# Stats endpoints
# ──────────────────────────────────────

class SellerSalesStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get(self, request):
        qs = SaleRecord.objects.filter(seller=request.user.seller_profile)
        return Response(_build_stats(qs))


class AdminSalesStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        qs = SaleRecord.objects.all()
        stats = _build_stats(qs, include_per_seller=True)
        stats['sellers_payout'] = _sellers_payout()
        return Response(stats)


# ──────────────────────────────────────
# Filtered sales lists
# ──────────────────────────────────────

def _apply_filters(qs, params):
    """Shared filter logic for both seller and admin sales lists."""
    date_from = params.get('date_from')
    date_to = params.get('date_to')
    product = params.get('product')
    channel = params.get('channel')
    search = params.get('search')

    if date_from:
        qs = qs.filter(sale_date__gte=date_from)
    if date_to:
        qs = qs.filter(sale_date__lte=date_to)
    if product:
        qs = qs.filter(variant__product__id=product)
    if channel:
        qs = qs.filter(channel=channel)
    if search:
        qs = qs.filter(
            Q(shopify_order_id__icontains=search)
            | Q(variant__sku__icontains=search)
            | Q(variant__product__name_en__icontains=search)
        )
    return qs


class SellerSalesListView(generics.ListAPIView):
    serializer_class = SaleRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_queryset(self):
        qs = SaleRecord.objects.filter(
            seller=self.request.user.seller_profile
        ).select_related('variant__product', 'seller')
        qs = _apply_filters(qs, self.request.query_params)
        return qs.order_by('-sale_date', '-id')


class AdminSalesListView(generics.ListAPIView):
    serializer_class = SaleRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        qs = SaleRecord.objects.all().select_related('variant__product', 'seller')
        seller = self.request.query_params.get('seller')
        if seller:
            qs = qs.filter(seller__id=seller)
        qs = _apply_filters(qs, self.request.query_params)
        return qs.order_by('-sale_date', '-id')