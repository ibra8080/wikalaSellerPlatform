from django.contrib import admin
from .models import Conversation, Message, Issue, IssueMessage, Notification


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('seller', 'subject', 'related_product', 'created_at')
    search_fields = ('seller__business_name', 'subject')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('issue_number', 'seller', 'title', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'category', 'priority')
    search_fields = ('issue_number', 'title', 'seller__business_name')
    readonly_fields = ('issue_number', 'created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')
    search_fields = ('user__email',)