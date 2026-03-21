"""
Django admin configuration for campaigns app.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Template, Campaign


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Admin configuration for Template model."""
    list_display = ['name', 'channel_type', 'version', 'is_active', 'usage_count', 'created_at']
    list_filter = ['channel_type', 'is_active']
    search_fields = ['name', 'content']
    ordering = ['channel_type', 'name']

    fieldsets = (
        (None, {
            'fields': ('name', 'channel_type', 'is_active', 'created_by')
        }),
        ('Content', {
            'fields': ('subject', 'content', 'variables')
        }),
        ('Version', {
            'fields': ('version',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def usage_count(self, obj):
        """Display usage count."""
        return obj.usage_count
    usage_count.short_description = 'Campaigns'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin configuration for Campaign model."""
    list_display = [
        'name', 'campaign_type', 'status', 'total_recipients',
        'sent_count', 'open_count', 'scheduled_at'
    ]
    list_filter = ['campaign_type', 'status']
    search_fields = ['name']
    filter_horizontal = ['segments']
    ordering = ['-created_at']
    readonly_fields = [
        'started_at', 'completed_at', 'sent_count',
        'open_count', 'click_count', 'bounce_count',
        'delivery_rate_display', 'open_rate_display',
        'click_rate_display', 'bounce_rate_display'
    ]

    fieldsets = (
        (None, {
            'fields': (
                'name', 'campaign_type', 'status',
                'template', 'channel', 'created_by'
            )
        }),
        ('Audience', {
            'fields': ('segments', 'total_recipients')
        }),
        ('Schedule', {
            'fields': ('scheduled_at', 'started_at', 'completed_at')
        }),
        ('Metrics', {
            'fields': (
                'sent_count', 'open_count', 'click_count', 'bounce_count',
                'delivery_rate_display', 'open_rate_display',
                'click_rate_display', 'bounce_rate_display'
            ),
            'classes': ('collapse',)
        }),
    )

    def delivery_rate_display(self, obj):
        """Display delivery rate as formatted percentage."""
        return format_html('<strong>{:.1f}%</strong>', obj.delivery_rate)
    delivery_rate_display.short_description = 'Delivery Rate'

    def open_rate_display(self, obj):
        """Display open rate as formatted percentage."""
        return format_html('<strong>{:.1f}%</strong>', obj.open_rate)
    open_rate_display.short_description = 'Open Rate'

    def click_rate_display(self, obj):
        """Display click rate as formatted percentage."""
        return format_html('<strong>{:.1f}%</strong>', obj.click_rate)
    click_rate_display.short_description = 'Click Rate'

    def bounce_rate_display(self, obj):
        """Display bounce rate as formatted percentage."""
        return format_html('<strong>{:.1f}%</strong>', obj.bounce_rate)
    bounce_rate_display.short_description = 'Bounce Rate'
