"""
Automations models - Automation, AutomationLog, Webhook, WebhookDelivery.
"""
from django.conf import settings
from django.core.validators import MinValueValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Automation(BaseModel):
    """
    Automation model for workflow automation rules.
    """
    class TriggerType(models.TextChoices):
        CONTACT_CREATED = 'CONTACT_CREATED', _('Contact Created')
        TAG_ADDED = 'TAG_ADDED', _('Tag Added')
        STAGE_CHANGED = 'STAGE_CHANGED', _('Stage Changed')
        DEAL_CREATED = 'DEAL_CREATED', _('Deal Created')
        FORM_SUBMITTED = 'FORM_SUBMITTED', _('Form Submitted')

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Automation Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    trigger_type = models.CharField(
        max_length=50,
        choices=TriggerType.choices,
        db_index=True,
        verbose_name=_('Trigger Type')
    )
    conditions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Conditions'),
        help_text=_('List of conditions that must be met for automation to run')
    )
    actions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Actions'),
        help_text=_('List of actions to execute when conditions are met')
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Active')
    )
    execution_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Execution Count')
    )
    last_executed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Executed At')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_automations',
        verbose_name=_('Created By')
    )

    class Meta:
        db_table = 'automations'
        verbose_name = _('Automation')
        verbose_name_plural = _('Automations')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trigger_type', 'is_active']),
            models.Index(fields=['is_active', 'last_executed_at']),
        ]

    def __str__(self):
        status = 'Active' if self.is_active else 'Inactive'
        return f"{self.name} ({status})"

    @property
    def has_conditions(self):
        """Check if automation has conditions defined."""
        return bool(self.conditions)

    @property
    def has_actions(self):
        """Check if automation has actions defined."""
        return bool(self.actions)

    @property
    def success_rate(self):
        """
        Calculate success rate based on execution logs.
        """
        if self.execution_count == 0:
            return 0.0

        successful = self.logs.filter(
            status=AutomationLog.Status.SUCCESS
        ).count()

        return (successful / self.execution_count) * 100

    def execute(self, trigger_data=None):
        """
        Execute automation with given trigger data.
        This is a placeholder - actual implementation would depend on
        the structure of conditions and actions.
        """
        from django.utils import timezone

        if not self.is_active:
            return None

        # Update execution metadata
        self.execution_count += 1
        self.last_executed_at = timezone.now()
        self.save(update_fields=['execution_count', 'last_executed_at'])

        # Create execution log
        log = AutomationLog.objects.create(
            automation=self,
            trigger_data=trigger_data or {},
            status=AutomationLog.Status.SUCCESS
        )

        return log


class AutomationLog(BaseModel):
    """
    Log entry for automation executions.
    """
    class Status(models.TextChoices):
        SUCCESS = 'SUCCESS', _('Success')
        PARTIAL = 'PARTIAL', _('Partial Success')
        FAILED = 'FAILED', _('Failed')

    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('Automation')
    )
    trigger_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Trigger Data')
    )
    actions_executed = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Actions Executed')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        db_index=True,
        verbose_name=_('Status')
    )
    error_message = models.TextField(
        blank=True,
        verbose_name=_('Error Message')
    )
    execution_time_ms = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Execution Time (ms)')
    )

    class Meta:
        db_table = 'automation_logs'
        verbose_name = _('Automation Log')
        verbose_name_plural = _('Automation Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['automation', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f"{self.automation.name} - {self.get_status_display()} at {self.created_at}"

    @property
    def is_successful(self):
        """Check if execution was successful."""
        return self.status == self.Status.SUCCESS

    @property
    def has_errors(self):
        """Check if execution had errors."""
        return bool(self.error_message)

    @property
    def execution_time_seconds(self):
        """Get execution time in seconds."""
        return self.execution_time_ms / 1000


class Webhook(BaseModel):
    """
    Webhook model for external integrations.
    """
    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Webhook Name')
    )
    url = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        verbose_name=_('Webhook URL')
    )
    events = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Events'),
        help_text=_('List of event types this webhook subscribes to')
    )
    secret = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Secret Key'),
        help_text=_('Secret key for signing webhook payloads')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Active')
    )
    last_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Triggered At')
    )
    failure_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Failure Count'),
        help_text=_('Consecutive failures - webhook disabled after threshold')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_webhooks',
        verbose_name=_('Created By')
    )

    class Meta:
        db_table = 'webhooks'
        verbose_name = _('Webhook')
        verbose_name_plural = _('Webhooks')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'last_triggered_at']),
        ]

    def __str__(self):
        status = 'Active' if self.is_active else 'Inactive'
        return f"{self.name} ({status})"

    @property
    def has_secret(self):
        """Check if webhook has a secret key configured."""
        return bool(self.secret)

    @property
    def is_failing(self):
        """Check if webhook has recent failures."""
        return self.failure_count > 0

    @property
    def success_rate(self):
        """Calculate success rate based on recent deliveries."""
        total = self.deliveries.count()
        if total == 0:
            return 0.0

        successful = self.deliveries.filter(success=True).count()
        return (successful / total) * 100

    def send(self, event, payload):
        """
        Send webhook payload for given event.
        This is a placeholder - actual implementation would use
        requests library or async HTTP client.
        """
        from django.utils import timezone
        import time

        if not self.is_active:
            return None

        if event not in self.events:
            return None

        # Create delivery record
        delivery = WebhookDelivery.objects.create(
            webhook=self,
            event=event,
            payload=payload
        )

        # Update last triggered timestamp
        self.last_triggered_at = timezone.now()
        self.save(update_fields=['last_triggered_at'])

        return delivery

    def increment_failure_count(self):
        """Increment failure count and disable if threshold exceeded."""
        self.failure_count += 1

        # Disable webhook after 10 consecutive failures
        if self.failure_count >= 10:
            self.is_active = False

        self.save(update_fields=['failure_count', 'is_active'])

    def reset_failure_count(self):
        """Reset failure count after successful delivery."""
        if self.failure_count > 0:
            self.failure_count = 0
            self.save(update_fields=['failure_count'])


class WebhookDelivery(BaseModel):
    """
    Log entry for webhook delivery attempts.
    """
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name=_('Webhook')
    )
    event = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Event')
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Payload')
    )
    response_status = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Response Status Code')
    )
    response_body = models.TextField(
        blank=True,
        verbose_name=_('Response Body')
    )
    success = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Success')
    )
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Attempted At')
    )

    class Meta:
        db_table = 'webhook_deliveries'
        verbose_name = _('Webhook Delivery')
        verbose_name_plural = _('Webhook Deliveries')
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['webhook', '-attempted_at']),
            models.Index(fields=['event', '-attempted_at']),
            models.Index(fields=['success', '-attempted_at']),
        ]

    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{self.webhook.name} - {self.event} ({status})"

    @property
    def is_successful(self):
        """Check if delivery was successful (2xx status code)."""
        if self.response_status is None:
            return False
        return 200 <= self.response_status < 300

    @property
    def is_client_error(self):
        """Check if delivery failed with client error (4xx)."""
        if self.response_status is None:
            return False
        return 400 <= self.response_status < 500

    @property
    def is_server_error(self):
        """Check if delivery failed with server error (5xx)."""
        if self.response_status is None:
            return False
        return self.response_status >= 500
