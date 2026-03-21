"""
Automations serializers.
"""
from rest_framework import serializers
from apps.automations.models import Automation, AutomationLog, Webhook, WebhookDelivery


class AutomationSerializer(serializers.ModelSerializer):
    """Full serializer for Automation."""

    class Meta:
        model = Automation
        fields = [
            'id', 'name', 'description', 'trigger_type', 'conditions', 'actions',
            'is_active', 'execution_count', 'last_executed_at', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'execution_count', 'last_executed_at', 'created_at', 'updated_at'
        ]


class AutomationListSerializer(serializers.ModelSerializer):
    """List serializer for Automation."""

    class Meta:
        model = Automation
        fields = [
            'id', 'name', 'trigger_type', 'is_active', 'execution_count',
            'last_executed_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'execution_count', 'last_executed_at', 'created_at'
        ]


class AutomationLogSerializer(serializers.ModelSerializer):
    """Serializer for AutomationLog (read-only)."""
    automation_name = serializers.CharField(source='automation.name', read_only=True)

    class Meta:
        model = AutomationLog
        fields = [
            'id', 'automation', 'automation_name', 'trigger_data', 'actions_executed',
            'status', 'error_message', 'execution_time_ms', 'created_at'
        ]
        read_only_fields = [
            'id', 'automation', 'automation_name', 'trigger_data', 'actions_executed',
            'status', 'error_message', 'execution_time_ms', 'created_at'
        ]


class WebhookSerializer(serializers.ModelSerializer):
    """Full serializer for Webhook."""
    secret = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Webhook
        fields = [
            'id', 'name', 'url', 'events', 'secret', 'is_active',
            'last_triggered_at', 'failure_count', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_triggered_at', 'failure_count', 'created_at', 'updated_at'
        ]


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for WebhookDelivery (read-only)."""
    webhook_name = serializers.CharField(source='webhook.name', read_only=True)

    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'webhook_name', 'event', 'payload',
            'response_status', 'response_body', 'success', 'attempted_at'
        ]
        read_only_fields = [
            'id', 'webhook', 'webhook_name', 'event', 'payload',
            'response_status', 'response_body', 'success', 'attempted_at'
        ]
