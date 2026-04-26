from rest_framework import serializers
from .models import Conversation, Message, Issue, IssueMessage, Notification


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'sender_email', 'content', 'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'sender_email', 'is_read', 'created_at')


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(
        source='seller.business_name', read_only=True
    )

    class Meta:
        model = Conversation
        fields = (
            'id', 'seller', 'seller_name', 'subject',
            'related_product', 'created_at', 'messages'
        )
        read_only_fields = ('id', 'seller', 'created_at')


class IssueMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.CharField(source='sender.email', read_only=True)

    class Meta:
        model = IssueMessage
        fields = ('id', 'sender', 'sender_email', 'content', 'created_at')
        read_only_fields = ('id', 'sender', 'sender_email', 'created_at')


class IssueSerializer(serializers.ModelSerializer):
    messages = IssueMessageSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(
        source='seller.business_name', read_only=True
    )

    class Meta:
        model = Issue
        fields = (
            'id', 'issue_number', 'seller', 'seller_name',
            'title', 'description', 'category', 'priority',
            'status', 'related_product', 'resolved_at',
            'created_at', 'updated_at', 'messages'
        )
        read_only_fields = (
            'id', 'issue_number', 'seller', 'seller_name',
            'resolved_at', 'created_at', 'updated_at'
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'id', 'type', 'title', 'body',
            'is_read', 'related_url', 'created_at'
        )
        read_only_fields = ('id', 'type', 'title', 'body', 'related_url', 'created_at')