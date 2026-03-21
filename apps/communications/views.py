"""
Communications views - ViewSets for Channel, EmailMessage, SMSMessage, WhatsAppMessage, ChatMessage.
"""
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from apps.communications.models import (
    Channel,
    EmailMessage,
    SMSMessage,
    WhatsAppMessage,
    ChatMessage,
)
from apps.communications.serializers import (
    ChannelSerializer,
    ChannelListSerializer,
    EmailMessageSerializer,
    EmailMessageListSerializer,
    SMSMessageSerializer,
    WhatsAppMessageSerializer,
    ChatMessageSerializer,
    EmailTrackingSerializer,
)
from apps.communications.filters import EmailMessageFilter, SMSMessageFilter


class ChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for Channel CRUD operations."""
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['channel_type', 'is_active']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return ChannelListSerializer
        return ChannelSerializer

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test channel connection (placeholder - implement provider-specific logic)."""
        channel = self.get_object()

        if not channel.is_active:
            return Response(
                {'error': 'Channel is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Placeholder implementation
        # In production, implement provider-specific connection tests
        # For email: try SMTP connection
        # For SMS/WhatsApp: validate API credentials
        # For chat: check WebSocket endpoint

        return Response({
            'success': True,
            'message': f'Connection test for {channel.name} would be performed here',
            'channel_type': channel.channel_type
        })


class EmailMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for EmailMessage CRUD operations with tracking."""
    queryset = EmailMessage.objects.select_related('channel', 'contact', 'sender').all()
    serializer_class = EmailMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = EmailMessageFilter
    search_fields = ['subject']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return EmailMessageListSerializer
        return EmailMessageSerializer

    def perform_create(self, serializer):
        """Auto-set sender on creation."""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Queue email for sending."""
        email = self.get_object()

        if email.status != EmailMessage.Status.DRAFT:
            return Response(
                {'error': 'Only draft emails can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # In production, integrate with email sending service (Celery task, etc.)
        email.status = EmailMessage.Status.QUEUED
        email.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': 'Email queued for sending',
            'tracking_id': str(email.tracking_id)
        })

    @action(detail=False, methods=['post'])
    def track(self, request):
        """Handle tracking pixel/click webhook."""
        serializer = EmailTrackingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tracking_id = serializer.validated_data['tracking_id']
        event = serializer.validated_data['event']
        timestamp = serializer.validated_data['timestamp']

        try:
            email = EmailMessage.objects.get(tracking_id=tracking_id)
        except EmailMessage.DoesNotExist:
            return Response(
                {'error': 'Email not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if event == 'opened':
            if not email.opened:
                email.opened = True
                email.first_opened_at = timestamp
            email.open_count += 1

        elif event == 'clicked':
            if not email.clicked:
                email.clicked = True
            email.click_count += 1

        email.save()

        return Response({'success': True})


class SMSMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for SMSMessage CRUD operations."""
    queryset = SMSMessage.objects.select_related('channel', 'contact', 'sender').all()
    serializer_class = SMSMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SMSMessageFilter

    def perform_create(self, serializer):
        """Auto-set sender and calculate segments on creation."""
        sms = serializer.save(sender=self.request.user)
        sms.segments = sms.calculate_segments()
        sms.save(update_fields=['segments'])

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Queue SMS for sending."""
        sms = self.get_object()

        if sms.status != SMSMessage.Status.DRAFT:
            return Response(
                {'error': 'Only draft SMS can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # In production, integrate with SMS provider (Twilio, etc.)
        sms.status = SMSMessage.Status.QUEUED
        sms.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': 'SMS queued for sending',
            'segments': sms.segments
        })


class WhatsAppMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for WhatsAppMessage CRUD operations."""
    queryset = WhatsAppMessage.objects.select_related('channel', 'contact', 'sender').all()
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'contact', 'media_type']

    def perform_create(self, serializer):
        """Auto-set sender on creation."""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Queue WhatsApp message for sending."""
        message = self.get_object()

        if message.status != WhatsAppMessage.Status.DRAFT:
            return Response(
                {'error': 'Only draft messages can be sent'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # In production, integrate with WhatsApp Business API
        message.status = WhatsAppMessage.Status.QUEUED
        message.save(update_fields=['status'])

        return Response({
            'success': True,
            'message': 'WhatsApp message queued for sending',
            'is_template': message.is_template_message,
            'has_media': message.has_media
        })


class ChatMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for ChatMessage CRUD operations."""
    queryset = ChatMessage.objects.select_related('channel', 'contact', 'sender').all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'read', 'contact']

    def perform_create(self, serializer):
        """Auto-set sender on creation."""
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark chat message as read."""
        message = self.get_object()

        if message.read:
            return Response({
                'success': True,
                'message': 'Message already marked as read'
            })

        message.mark_as_read()

        serializer = self.get_serializer(message)
        return Response(serializer.data)
