"""
Communications models - Channel, Communication (abstract), EmailMessage, SMSMessage, WhatsAppMessage, ChatMessage.
"""
import uuid
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Channel(BaseModel):
    """
    Communication channel model - supports email, SMS, WhatsApp, and chat.
    """
    class ChannelType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        WHATSAPP = 'WHATSAPP', _('WhatsApp')
        CHAT = 'CHAT', _('Chat')

    name = models.CharField(
        max_length=100,
        verbose_name=_('Channel Name')
    )
    channel_type = models.CharField(
        max_length=20,
        choices=ChannelType.choices,
        db_index=True,
        verbose_name=_('Channel Type')
    )
    configuration = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Configuration'),
        help_text=_('Channel-specific configuration (e.g., SMTP settings, API endpoints)')
    )
    credentials = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Credentials'),
        help_text=_('API keys, tokens, passwords (should be encrypted in production)')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Active')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_channels',
        verbose_name=_('Owner')
    )

    class Meta:
        db_table = 'channels'
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')
        ordering = ['channel_type', 'name']
        indexes = [
            models.Index(fields=['channel_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"

    @property
    def message_count(self):
        """Return total messages sent through this channel."""
        # This would need to aggregate across all message types
        # Placeholder implementation
        return 0


class Communication(BaseModel):
    """
    Abstract base model for all communication types.
    """
    class Direction(models.TextChoices):
        INBOUND = 'INBOUND', _('Inbound')
        OUTBOUND = 'OUTBOUND', _('Outbound')

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        QUEUED = 'QUEUED', _('Queued')
        SENT = 'SENT', _('Sent')
        DELIVERED = 'DELIVERED', _('Delivered')
        FAILED = 'FAILED', _('Failed')
        BOUNCED = 'BOUNCED', _('Bounced')

    channel = models.ForeignKey(
        Channel,
        on_delete=models.PROTECT,
        related_name='%(class)s_messages',
        verbose_name=_('Channel')
    )
    contact = models.ForeignKey(
        'contacts.Contact',
        on_delete=models.CASCADE,
        related_name='%(class)s_messages',
        verbose_name=_('Contact')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_%(class)s_messages',
        verbose_name=_('Sender')
    )
    direction = models.CharField(
        max_length=20,
        choices=Direction.choices,
        default=Direction.OUTBOUND,
        db_index=True,
        verbose_name=_('Direction')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name=_('Status')
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_direction_display()} {self.__class__.__name__} to {self.contact.name}"

    @property
    def is_sent(self):
        """Check if message has been sent."""
        return self.status in [
            self.Status.SENT,
            self.Status.DELIVERED
        ]

    @property
    def is_failed(self):
        """Check if message delivery failed."""
        return self.status in [
            self.Status.FAILED,
            self.Status.BOUNCED
        ]


class EmailMessage(Communication):
    """
    Email message model with tracking capabilities.
    """
    subject = models.CharField(
        max_length=500,
        verbose_name=_('Subject')
    )
    body_html = models.TextField(
        verbose_name=_('HTML Body')
    )
    body_text = models.TextField(
        blank=True,
        verbose_name=_('Plain Text Body')
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Attachments'),
        help_text=_('List of attachment metadata')
    )
    tracking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        verbose_name=_('Tracking ID')
    )
    opened = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Opened')
    )
    open_count = models.IntegerField(
        default=0,
        verbose_name=_('Open Count')
    )
    first_opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('First Opened At')
    )
    clicked = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Clicked')
    )
    click_count = models.IntegerField(
        default=0,
        verbose_name=_('Click Count')
    )

    class Meta:
        db_table = 'email_messages'
        verbose_name = _('Email Message')
        verbose_name_plural = _('Email Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['tracking_id']),
            models.Index(fields=['opened', 'created_at']),
            models.Index(fields=['contact', 'status']),
        ]

    def __str__(self):
        return f"Email to {self.contact.email}: {self.subject}"

    @property
    def has_attachments(self):
        """Check if email has attachments."""
        return bool(self.attachments)

    @property
    def engagement_score(self):
        """Calculate engagement score based on opens and clicks."""
        score = 0
        if self.opened:
            score += 1
        score += min(self.open_count, 5) * 0.2
        if self.clicked:
            score += 2
        score += min(self.click_count, 5) * 0.4
        return min(score, 10)


class SMSMessage(Communication):
    """
    SMS message model with provider integration.
    """
    body = models.TextField(
        max_length=1600,
        verbose_name=_('Message Body'),
        help_text=_('Maximum 1600 characters (10 segments)')
    )
    provider_message_id = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name=_('Provider Message ID')
    )
    provider_status = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Provider Status')
    )
    segments = models.IntegerField(
        default=1,
        verbose_name=_('Message Segments')
    )

    class Meta:
        db_table = 'sms_messages'
        verbose_name = _('SMS Message')
        verbose_name_plural = _('SMS Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_message_id']),
            models.Index(fields=['contact', 'status']),
        ]

    def __str__(self):
        preview = self.body[:50] + '...' if len(self.body) > 50 else self.body
        return f"SMS to {self.contact.phone}: {preview}"

    @property
    def character_count(self):
        """Return character count of the message."""
        return len(self.body)

    def calculate_segments(self):
        """Calculate number of SMS segments based on character count."""
        char_count = len(self.body)
        if char_count <= 160:
            return 1
        return (char_count - 1) // 153 + 1


class WhatsAppMessage(Communication):
    """
    WhatsApp message model supporting text, media, and templates.
    """
    class MediaType(models.TextChoices):
        NONE = 'NONE', _('None')
        IMAGE = 'IMAGE', _('Image')
        VIDEO = 'VIDEO', _('Video')
        DOCUMENT = 'DOCUMENT', _('Document')
        AUDIO = 'AUDIO', _('Audio')

    body = models.TextField(
        blank=True,
        verbose_name=_('Message Body')
    )
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.NONE,
        verbose_name=_('Media Type')
    )
    media_url = models.URLField(
        blank=True,
        verbose_name=_('Media URL')
    )
    template_name = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name=_('Template Name')
    )
    template_params = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Template Parameters')
    )

    class Meta:
        db_table = 'whatsapp_messages'
        verbose_name = _('WhatsApp Message')
        verbose_name_plural = _('WhatsApp Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['template_name']),
            models.Index(fields=['contact', 'status']),
        ]

    def __str__(self):
        if self.template_name:
            return f"WhatsApp to {self.contact.phone}: Template {self.template_name}"
        preview = self.body[:50] + '...' if len(self.body) > 50 else self.body
        return f"WhatsApp to {self.contact.phone}: {preview}"

    @property
    def is_template_message(self):
        """Check if this is a template-based message."""
        return bool(self.template_name)

    @property
    def has_media(self):
        """Check if message includes media."""
        return self.media_type != self.MediaType.NONE


class ChatMessage(Communication):
    """
    Chat message model for real-time messaging.
    """
    body = models.TextField(
        verbose_name=_('Message Body')
    )
    room = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Chat Room')
    )
    read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Read')
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Read At')
    )

    class Meta:
        db_table = 'chat_messages'
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['room', '-created_at']),
            models.Index(fields=['room', 'read']),
            models.Index(fields=['contact', 'status']),
        ]

    def __str__(self):
        preview = self.body[:50] + '...' if len(self.body) > 50 else self.body
        return f"Chat in {self.room}: {preview}"

    def mark_as_read(self):
        """Mark message as read."""
        if not self.read:
            from django.utils import timezone
            self.read = True
            self.read_at = timezone.now()
            self.save(update_fields=['read', 'read_at'])
