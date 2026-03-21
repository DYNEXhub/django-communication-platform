"""
Campaigns models - Template, Campaign.
"""
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Template(BaseModel):
    """
    Message template model for reusable content across channels.
    """
    class ChannelType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        WHATSAPP = 'WHATSAPP', _('WhatsApp')

    name = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name=_('Template Name')
    )
    channel_type = models.CharField(
        max_length=20,
        choices=ChannelType.choices,
        db_index=True,
        verbose_name=_('Channel Type')
    )
    subject = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Subject'),
        help_text=_('For email templates only')
    )
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Template content with variable placeholders (e.g., {{first_name}})')
    )
    variables = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Variables'),
        help_text=_('List of variable names used in the template')
    )
    version = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Version')
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Active')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_templates',
        verbose_name=_('Created By')
    )

    class Meta:
        db_table = 'templates'
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
        ordering = ['channel_type', 'name']
        indexes = [
            models.Index(fields=['channel_type', 'is_active']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_channel_type_display()})"

    @property
    def variable_count(self):
        """Return the number of variables in this template."""
        return len(self.variables)

    @property
    def usage_count(self):
        """Return the number of campaigns using this template."""
        return self.campaigns.count()

    def clone(self, new_name=None):
        """
        Create a copy of this template with incremented version.
        """
        new_template = Template.objects.create(
            name=new_name or f"{self.name} (Copy)",
            channel_type=self.channel_type,
            subject=self.subject,
            content=self.content,
            variables=self.variables,
            version=self.version + 1,
            is_active=True,
            created_by=self.created_by
        )
        return new_template


class Campaign(BaseModel):
    """
    Campaign model for managing bulk message sending operations.
    """
    class CampaignType(models.TextChoices):
        EMAIL = 'EMAIL', _('Email')
        SMS = 'SMS', _('SMS')
        WHATSAPP = 'WHATSAPP', _('WhatsApp')

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SCHEDULED = 'SCHEDULED', _('Scheduled')
        RUNNING = 'RUNNING', _('Running')
        PAUSED = 'PAUSED', _('Paused')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Campaign Name')
    )
    campaign_type = models.CharField(
        max_length=20,
        choices=CampaignType.choices,
        db_index=True,
        verbose_name=_('Campaign Type')
    )
    template = models.ForeignKey(
        Template,
        on_delete=models.PROTECT,
        related_name='campaigns',
        verbose_name=_('Template')
    )
    channel = models.ForeignKey(
        'communications.Channel',
        on_delete=models.PROTECT,
        related_name='campaigns',
        verbose_name=_('Channel')
    )
    segments = models.ManyToManyField(
        'contacts.ContactGroup',
        blank=True,
        related_name='campaigns',
        verbose_name=_('Target Segments')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name=_('Status')
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Scheduled At')
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Started At')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )
    total_recipients = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Total Recipients')
    )
    sent_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Sent Count')
    )
    open_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Open Count')
    )
    click_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Click Count')
    )
    bounce_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Bounce Count')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_campaigns',
        verbose_name=_('Created By')
    )

    class Meta:
        db_table = 'campaigns'
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'scheduled_at']),
            models.Index(fields=['campaign_type', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def is_active(self):
        """Check if campaign is currently active."""
        return self.status in [
            self.Status.SCHEDULED,
            self.Status.RUNNING
        ]

    @property
    def is_completed(self):
        """Check if campaign is completed."""
        return self.status in [
            self.Status.COMPLETED,
            self.Status.CANCELLED
        ]

    @property
    def delivery_rate(self):
        """Calculate delivery rate percentage."""
        if self.total_recipients == 0:
            return 0.0
        return (self.sent_count / self.total_recipients) * 100

    @property
    def open_rate(self):
        """Calculate open rate percentage (for email campaigns)."""
        if self.sent_count == 0:
            return 0.0
        return (self.open_count / self.sent_count) * 100

    @property
    def click_rate(self):
        """Calculate click rate percentage (for email campaigns)."""
        if self.sent_count == 0:
            return 0.0
        return (self.click_count / self.sent_count) * 100

    @property
    def bounce_rate(self):
        """Calculate bounce rate percentage."""
        if self.sent_count == 0:
            return 0.0
        return (self.bounce_count / self.sent_count) * 100

    @property
    def progress_percentage(self):
        """Calculate campaign progress percentage."""
        if self.total_recipients == 0:
            return 0.0
        return (self.sent_count / self.total_recipients) * 100

    def calculate_total_recipients(self):
        """
        Calculate total recipients based on selected segments.
        """
        from django.db.models import Q

        if not self.segments.exists():
            return 0

        # Get unique contacts from all segments
        contact_ids = set()
        for segment in self.segments.all():
            contact_ids.update(
                segment.contacts.filter(
                    status='ACTIVE'
                ).values_list('id', flat=True)
            )

        return len(contact_ids)

    def start(self):
        """
        Start the campaign execution.
        """
        from django.utils import timezone

        if self.status != self.Status.SCHEDULED:
            return False

        self.status = self.Status.RUNNING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
        return True

    def pause(self):
        """
        Pause the campaign execution.
        """
        if self.status != self.Status.RUNNING:
            return False

        self.status = self.Status.PAUSED
        self.save(update_fields=['status'])
        return True

    def complete(self):
        """
        Mark campaign as completed.
        """
        from django.utils import timezone

        if self.status not in [self.Status.RUNNING, self.Status.PAUSED]:
            return False

        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
        return True
