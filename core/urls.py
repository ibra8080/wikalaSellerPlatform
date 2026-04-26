from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/sellers/', include('apps.sellers.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/communication/', include('apps.communication.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/contracts/', include('apps.contracts.urls')),
]