from django.contrib import admin
from .models import WiderrufRequest


@admin.register(WiderrufRequest)
class WiderrufRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'bestellnummer', 'email', 'created_at', 'confirmation_sent')
    list_filter = ('confirmation_sent', 'created_at')
    search_fields = ('name', 'email', 'bestellnummer')
    readonly_fields = ('name', 'email', 'bestellnummer', 'widerrufserklaerung',
                       'created_at', 'confirmation_sent', 'raw_ip', 'user_agent')

    def has_add_permission(self, request):
        return False  # records are created only via the public endpoint

    def has_change_permission(self, request, obj=None):
        return False  # legal records are immutable