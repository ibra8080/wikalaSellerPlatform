from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, Issue, IssueMessage, Notification
from .serializers import (
    ConversationSerializer, MessageSerializer,
    IssueSerializer, IssueMessageSerializer, NotificationSerializer
)
from apps.sellers.views import IsSeller, IsAdmin
import django.utils.timezone as timezone


# ──────────────────────────────────────
# Conversations
# ──────────────────────────────────────

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Conversation.objects.all().order_by('-created_at')
        return Conversation.objects.filter(
            seller=user.seller_profile
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Conversation.objects.all()
        return Conversation.objects.filter(seller=user.seller_profile)


class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            conversation = Conversation.objects.get(id=self.kwargs['pk'])
        except Conversation.DoesNotExist:
            raise NotFound('Conversation not found.')

        user = self.request.user
        is_admin = user.role == 'admin' or user.is_superuser
        is_owner = hasattr(user, 'seller_profile') and \
            conversation.seller_id == user.seller_profile.id
        if not (is_admin or is_owner):
            raise PermissionDenied('You do not have access to this conversation.')

        serializer.save(sender=user, conversation=conversation)


class ConversationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        conversation = get_object_or_404(Conversation, id=pk)

        if request.user.role != 'admin' and conversation.seller != request.user.seller_profile:
            raise PermissionDenied()

        conversation.messages.exclude(sender=request.user).update(is_read=True)
        return Response({'status': 'messages marked as read'})


# ──────────────────────────────────────
# Issues
# ──────────────────────────────────────

class IssueListCreateView(generics.ListCreateAPIView):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Issue.objects.all().order_by('-created_at')
        return Issue.objects.filter(
            seller=user.seller_profile
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user.seller_profile)


class IssueDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Issue.objects.all()
        return Issue.objects.filter(seller=user.seller_profile)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == 'resolved' and not instance.resolved_at:
            instance.resolved_at = timezone.now()
            instance.save()


class IssueMessageCreateView(generics.CreateAPIView):
    serializer_class = IssueMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            issue = Issue.objects.get(id=self.kwargs['pk'])
        except Issue.DoesNotExist:
            raise NotFound('Issue not found.')

        user = self.request.user
        is_admin = user.role == 'admin' or user.is_superuser
        is_owner = hasattr(user, 'seller_profile') and \
            issue.seller_id == user.seller_profile.id
        if not (is_admin or is_owner):
            raise PermissionDenied('You do not have access to this issue.')

        serializer.save(sender=user, issue=issue)


# ──────────────────────────────────────
# Notifications
# ──────────────────────────────────────

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = get_object_or_404(
            Notification, id=pk, user=request.user
        )
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})