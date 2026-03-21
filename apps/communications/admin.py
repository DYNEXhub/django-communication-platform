"""
Django admin configuration for communications app.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Channel, EmailMessage, SMSMessage, WhatsAppMessage, ChatMessage


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin configuration for Channel model."""
    list_display = ['name', 'channel_type', 'is_active', 'created_at']
    list_filter = ['channel_type', 'is_active']
    search_fields = ['name']
    ordering = ['channel_type', 'name']

    fieldsets = (
        (None, {
            'fields': ('name', 'channel_type', 'is_active', 'owner')
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_exclude(self, request, obj=None):
        """Exclude credentials field from admin display for security."""
        return ['credentials']


@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    """Admin configuration for EmailMessage model."""
    list_display = ['subject', 'contact', 'status', 'opened', 'open_count', 'created_at']
    list_filter = ['status', 'opened', 'clicked']
    search_fields = ['subject', 'contact__email', 'contact__name']
    ordering = ['-created_at']
    readonly_fields = [
        'tracking_id', 'open_count', 'first_opened_at',
        'click_count', 'created_at', 'updated_at'
    ]

    fieldsets = (
        (None, {
            'fields': ('channel', 'contact', 'sender', 'direction', 'status')
        }),
        ('Content', {
            'fields': ('subject', 'body_html', 'body_text', 'attachments')
        }),
        ('Tracking', {
            'fields': (
                'tracking_id', 'opened', 'open_count', 'first_opened_at',
                'clicked', 'click_count'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    """Admin configuration for SMSMessage model."""
    list_display = ['contact', 'body_preview', 'status', 'segments', 'created_at']
    list_filter = ['status', 'segments']
    search_fields = ['contact__phone', 'contact__name', 'body']
    ordering = ['-created_at']
    readonly_fields = ['provider_message_id', 'created_at', 'updated_at']

    def body_preview(self, obj):
        """Display body preview."""
        preview = obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
        return preview
    body_preview.short_description = 'Body'


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    """Admin configuration for WhatsAppMessage model."""
    list_display = ['contact', 'body_preview', 'media_type', 'status', 'created_at']
    list_filter = ['status', 'media_type']
    search_fields = ['contact__phone', 'contact__name', 'body', 'template_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('channel', 'contact', 'sender', 'direction', 'status')
        }),
        ('Content', {
            'fields': ('body', 'media_type', 'media_url')
        }),
        ('Template', {
            'fields': ('template_name', 'template_params'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def body_preview(self, obj):
        """Display body preview."""
        if obj.template_name:
            return f'Template: {obj.template_name}'
        preview = obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
        return preview
    body_preview.short_description = 'Content'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin configuration for ChatMessage model."""
    list_display = ['contact', 'room', 'body_preview', 'read', 'created_at']
    list_filter = ['read', 'room']
    search_fields = ['contact__name', 'body', 'room']
    ordering = ['-created_at']
    readonly_fields = ['read_at', 'created_at', 'updated_at']

    def body_preview(self, obj):
        """Display body preview."""
        preview = obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
        return preview
    body_preview.short_description = 'Message'
