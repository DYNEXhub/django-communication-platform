"""
Django admin configuration for automations app.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Automation, AutomationLog, Webhook, WebhookDelivery


@admin.register(Automation)
class AutomationAdmin(admin.ModelAdmin):
    """Admin configuration for Automation model."""
    list_display = [
        'name', 'trigger_type', 'is_active',
        'execution_count', 'success_rate_display', 'last_executed_at'
    ]
    list_filter = ['trigger_type', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    readonly_fields = ['execution_count', 'last_executed_at', 'success_rate_display']

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'trigger_type', 'is_active', 'created_by')
        }),
        ('Configuration', {
            'fields': ('conditions', 'actions')
        }),
        ('Execution Metrics', {
            'fields': ('execution_count', 'last_executed_at', 'success_rate_display'),
            'classes': ('collapse',)
        }),
    )

    def success_rate_display(self, obj):
        """Display success rate as formatted percentage."""
        return format_html('<strong>{:.1f}%</strong>', obj.success_rate)
    success_rate_display.short_description = 'Success Rate'


@admin.register(AutomationLog)
class AutomationLogAdmin(admin.ModelAdmin):
    """Admin configuration for AutomationLog model."""
    list_display = [
        'automation', 'status', 'execution_time_ms', 'created_at'
    ]
    list_filter = ['status', 'automation']
    search_fields = ['automation__name', 'error_message']
    ordering = ['-created_at']
    readonly_fields = [
        'automation', 'trigger_data', 'actions_executed',
        'status', 'error_message', 'execution_time_ms',
        'created_at', 'updated_at', 'execution_time_seconds_display'
    ]

    fieldsets = (
        (None, {
            'fields': ('automation', 'status', 'created_at')
        }),
        ('Execution Data', {
            'fields': ('trigger_data', 'actions_executed'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('execution_time_ms', 'execution_time_seconds_display')
        }),
        ('Error Details', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of logs."""
        return False

    def execution_time_seconds_display(self, obj):
        """Display execution time in seconds."""
        return format_html('<strong>{:.3f}s</strong>', obj.execution_time_seconds)
    execution_time_seconds_display.short_description = 'Execution Time (seconds)'


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin configuration for Webhook model."""
    list_display = [
        'name', 'url', 'is_active',
        'failure_count', 'success_rate_display', 'last_triggered_at'
    ]
    list_filter = ['is_active']
    search_fields = ['name', 'url']
    ordering = ['-created_at']
    readonly_fields = ['last_triggered_at', 'failure_count', 'success_rate_display']

    fieldsets = (
        (None, {
            'fields': ('name', 'url', 'is_active', 'created_by')
        }),
        ('Configuration', {
            'fields': ('events', 'secret')
        }),
        ('Metrics', {
            'fields': ('last_triggered_at', 'failure_count', 'success_rate_display'),
            'classes': ('collapse',)
        }),
    )

    def success_rate_display(self, obj):
        """Display success rate as formatted percentage."""
        return format_html('<strong>{:.1f}%</strong>', obj.success_rate)
    success_rate_display.short_description = 'Success Rate'


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    """Admin configuration for WebhookDelivery model."""
    list_display = [
        'webhook', 'event', 'response_status',
        'success', 'attempted_at'
    ]
    list_filter = ['success', 'event', 'webhook']
    search_fields = ['webhook__name', 'event']
    ordering = ['-attempted_at']
    readonly_fields = [
        'webhook', 'event', 'payload', 'response_status',
        'response_body', 'success', 'attempted_at', 'created_at'
    ]

    fieldsets = (
        (None, {
            'fields': ('webhook', 'event', 'success', 'attempted_at')
        }),
        ('Request', {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        ('Response', {
            'fields': ('response_status', 'response_body')
        }),
    )

    def has_add_permission(self, request):
        """Disable manual creation of deliveries."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of deliveries."""
        return False
