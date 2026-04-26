from django.urls import path
from .views import (
    ConversationListCreateView, ConversationDetailView, MessageCreateView,
    IssueListCreateView, IssueDetailView, IssueMessageCreateView,
    NotificationListView, NotificationMarkReadView
)

urlpatterns = [
    # Conversations
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/messages/', MessageCreateView.as_view(), name='message-create'),

    # Issues
    path('issues/', IssueListCreateView.as_view(), name='issue-list'),
    path('issues/<int:pk>/', IssueDetailView.as_view(), name='issue-detail'),
    path('issues/<int:pk>/messages/', IssueMessageCreateView.as_view(), name='issue-message-create'),

    # Notifications
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
]