"""
Communications serializers - Channel, EmailMessage, SMSMessage, WhatsAppMessage, ChatMessage.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.communications.models import (
    Channel,
    EmailMessage,
    SMSMessage,
    WhatsAppMessage,
    ChatMessage,
)

User = get_user_model()


class ChannelListSerializer(serializers.ModelSerializer):
    """Simplified channel serializer for list views."""
    class Meta:
        model = Channel
        fields = ['id', 'name', 'channel_type', 'is_active', 'created_at']


class ChannelSerializer(serializers.ModelSerializer):
    """Full channel serializer with credentials write-only."""
    class Meta:
        model = Channel
        fields = [
            'id', 'name', 'channel_type', 'configuration', 'credentials',
            'is_active', 'owner', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'credentials': {'write_only': True}
        }


class SimpleContactSerializer(serializers.Serializer):
    """Simple contact serializer for nested representation."""
    name = serializers.CharField()
    email = serializers.EmailField()


class EmailMessageListSerializer(serializers.ModelSerializer):
    """Simplified email message serializer for list views."""
    contact = SimpleContactSerializer(read_only=True)

    class Meta:
        model = EmailMessage
        fields = ['id', 'subject', 'contact', 'status', 'opened', 'created_at']


class EmailMessageSerializer(serializers.ModelSerializer):
    """Full email message serializer with tracking."""
    channel_id = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(),
        source='channel',
        write_only=True
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset='contacts.Contact',
        source='contact',
        write_only=True
    )

    class Meta:
        model = EmailMessage
        fields = [
            'id', 'channel', 'channel_id', 'contact', 'contact_id', 'sender',
            'direction', 'status', 'subject', 'body_html', 'body_text',
            'attachments', 'tracking_id', 'opened', 'open_count',
            'first_opened_at', 'clicked', 'click_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'tracking_id', 'opened', 'open_count', 'first_opened_at',
            'clicked', 'click_count', 'created_at', 'updated_at'
        ]


class SMSMessageSerializer(serializers.ModelSerializer):
    """SMS message serializer."""
    channel_id = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(),
        source='channel',
        write_only=True
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset='contacts.Contact',
        source='contact',
        write_only=True
    )

    class Meta:
        model = SMSMessage
        fields = [
            'id', 'channel', 'channel_id', 'contact', 'contact_id', 'sender',
            'direction', 'status', 'body', 'provider_message_id',
            'provider_status', 'segments', 'created_at'
        ]
        read_only_fields = [
            'id', 'status', 'provider_message_id', 'provider_status', 'created_at'
        ]

    def validate_body(self, value):
        """Validate SMS body length."""
        if len(value) > 1600:
            raise serializers.ValidationError(
                'SMS body cannot exceed 1600 characters (10 segments)'
            )
        return value


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    """WhatsApp message serializer."""
    channel_id = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(),
        source='channel',
        write_only=True
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset='contacts.Contact',
        source='contact',
        write_only=True
    )

    class Meta:
        model = WhatsAppMessage
        fields = [
            'id', 'channel', 'channel_id', 'contact', 'contact_id', 'sender',
            'direction', 'status', 'body', 'media_type', 'media_url',
            'template_name', 'template_params', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, data):
        """Validate WhatsApp message structure."""
        media_type = data.get('media_type')
        media_url = data.get('media_url')
        body = data.get('body')
        template_name = data.get('template_name')

        # If media_type is not NONE, media_url is required
        if media_type != WhatsAppMessage.MediaType.NONE and not media_url:
            raise serializers.ValidationError(
                'media_url is required when media_type is not NONE'
            )

        # Either body or template_name must be provided
        if not body and not template_name:
            raise serializers.ValidationError(
                'Either body or template_name must be provided'
            )

        return data


class ChatMessageSerializer(serializers.ModelSerializer):
    """Chat message serializer."""
    channel_id = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(),
        source='channel',
        write_only=True
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset='contacts.Contact',
        source='contact',
        write_only=True
    )

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'channel', 'channel_id', 'contact', 'contact_id', 'sender',
            'direction', 'status', 'body', 'room', 'read', 'read_at', 'created_at'
        ]
        read_only_fields = ['id', 'read', 'read_at', 'created_at']


class EmailTrackingSerializer(serializers.Serializer):
    """Serializer for email tracking webhook callbacks."""
    tracking_id = serializers.UUIDField()
    event = serializers.ChoiceField(choices=['opened', 'clicked'])
    timestamp = serializers.DateTimeField()
    metadata = serializers.JSONField(required=False, default=dict)
