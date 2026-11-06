from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def paginate_queryset(self, queryset, request, view=None):
        # Opt-in: only paginate when ?page= is present. Without it the
        # endpoint returns the full array, so the other ~10 consumers
        # (dashboards, sales, shipment form, etc.) keep working unchanged.
        if 'page' not in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)
