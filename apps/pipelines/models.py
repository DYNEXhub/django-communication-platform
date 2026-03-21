"""
Pipelines models - Pipeline, PipelineStage, Deal, Interaction.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Pipeline(BaseModel):
    """
    Pipeline model for organizing sales/deal stages.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Pipeline Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    is_default = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Default Pipeline')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_pipelines',
        verbose_name=_('Created By')
    )

    class Meta:
        db_table = 'pipelines'
        verbose_name = _('Pipeline')
        verbose_name_plural = _('Pipelines')
        ordering = ['-is_default', 'name']

    def __str__(self):
        default_marker = ' (Default)' if self.is_default else ''
        return f"{self.name}{default_marker}"

    @property
    def stage_count(self):
        """Return the number of stages in this pipeline."""
        return self.stages.count()

    @property
    def deal_count(self):
        """Return the total number of deals in this pipeline."""
        return Deal.objects.filter(stage__pipeline=self).count()

    def save(self, *args, **kwargs):
        """Ensure only one default pipeline exists."""
        if self.is_default:
            # Set all other pipelines to not default
            Pipeline.objects.filter(is_default=True).exclude(
                id=self.id
            ).update(is_default=False)
        super().save(*args, **kwargs)


class PipelineStage(BaseModel):
    """
    Pipeline stage model representing a step in the sales process.
    """
    pipeline = models.ForeignKey(
        Pipeline,
        on_delete=models.CASCADE,
        related_name='stages',
        verbose_name=_('Pipeline')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Stage Name')
    )
    order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Order')
    )
    probability = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Win Probability (%)'),
        help_text=_('Likelihood of closing deals in this stage (0-100%)')
    )
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message=_('Color must be a valid hex color code (e.g., #6366f1)')
            )
        ],
        verbose_name=_('Color')
    )

    class Meta:
        db_table = 'pipeline_stages'
        verbose_name = _('Pipeline Stage')
        verbose_name_plural = _('Pipeline Stages')
        ordering = ['order']
        unique_together = [['pipeline', 'order']]
        indexes = [
            models.Index(fields=['pipeline', 'order']),
        ]

    def __str__(self):
        return f"{self.pipeline.name} - {self.name} ({self.probability}%)"

    @property
    def deal_count(self):
        """Return the number of deals in this stage."""
        return self.deals.filter(status=Deal.Status.OPEN).count()

    @property
    def total_value(self):
        """Return the total value of all deals in this stage."""
        from django.db.models import Sum
        return self.deals.filter(
            status=Deal.Status.OPEN
        ).aggregate(
            total=Sum('value')
        )['total'] or 0


class Deal(BaseModel):
    """
    Deal model representing a sales opportunity.
    """
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        WON = 'WON', _('Won')
        LOST = 'LOST', _('Lost')

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Deal Name')
    )
    value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Deal Value')
    )
    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.PROTECT,
        related_name='deals',
        verbose_name=_('Pipeline Stage')
    )
    contact = models.ForeignKey(
        'contacts.Contact',
        on_delete=models.CASCADE,
        related_name='deals',
        verbose_name=_('Contact')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deals',
        verbose_name=_('Owner')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
        verbose_name=_('Status')
    )
    probability = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Win Probability (%)')
    )
    expected_close_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Expected Close Date')
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Closed At')
    )
    lost_reason = models.TextField(
        blank=True,
        verbose_name=_('Lost Reason')
    )

    class Meta:
        db_table = 'deals'
        verbose_name = _('Deal')
        verbose_name_plural = _('Deals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'stage']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['expected_close_date']),
            models.Index(fields=['contact', 'status']),
        ]

    def __str__(self):
        return f"{self.name} - ${self.value} ({self.get_status_display()})"

    @property
    def is_open(self):
        """Check if deal is still open."""
        return self.status == self.Status.OPEN

    @property
    def is_won(self):
        """Check if deal was won."""
        return self.status == self.Status.WON

    @property
    def is_lost(self):
        """Check if deal was lost."""
        return self.status == self.Status.LOST

    @property
    def weighted_value(self):
        """Calculate weighted value based on probability."""
        return float(self.value) * (self.probability / 100)

    @property
    def days_in_stage(self):
        """Calculate how many days the deal has been in current stage."""
        from django.utils import timezone
        from datetime import datetime

        # This would require tracking stage changes
        # For now, return days since deal creation
        delta = timezone.now() - self.created_at
        return delta.days

    @property
    def pipeline(self):
        """Get the pipeline this deal belongs to."""
        return self.stage.pipeline

    def move_to_stage(self, new_stage):
        """
        Move deal to a new stage and update probability.
        """
        if new_stage.pipeline != self.stage.pipeline:
            raise ValueError("Cannot move deal to a stage in a different pipeline")

        self.stage = new_stage
        self.probability = new_stage.probability
        self.save(update_fields=['stage', 'probability'])

    def mark_won(self):
        """
        Mark deal as won.
        """
        from django.utils import timezone

        self.status = self.Status.WON
        self.probability = 100
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'probability', 'closed_at'])

    def mark_lost(self, reason=''):
        """
        Mark deal as lost with optional reason.
        """
        from django.utils import timezone

        self.status = self.Status.LOST
        self.probability = 0
        self.closed_at = timezone.now()
        self.lost_reason = reason
        self.save(update_fields=['status', 'probability', 'closed_at', 'lost_reason'])


class Interaction(BaseModel):
    """
    Interaction model for tracking contact touchpoints.
    """
    class InteractionType(models.TextChoices):
        CALL = 'CALL', _('Phone Call')
        MEETING = 'MEETING', _('Meeting')
        EMAIL = 'EMAIL', _('Email')
        NOTE = 'NOTE', _('Note')
        TASK = 'TASK', _('Task')

    contact = models.ForeignKey(
        'contacts.Contact',
        on_delete=models.CASCADE,
        related_name='interactions',
        verbose_name=_('Contact')
    )
    deal = models.ForeignKey(
        Deal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions',
        verbose_name=_('Deal')
    )
    interaction_type = models.CharField(
        max_length=20,
        choices=InteractionType.choices,
        db_index=True,
        verbose_name=_('Type')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='interactions',
        verbose_name=_('Agent')
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('Scheduled At')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )

    class Meta:
        db_table = 'interactions'
        verbose_name = _('Interaction')
        verbose_name_plural = _('Interactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contact', '-created_at']),
            models.Index(fields=['deal', '-created_at']),
            models.Index(fields=['agent', 'scheduled_at']),
            models.Index(fields=['interaction_type', 'scheduled_at']),
        ]

    def __str__(self):
        type_display = self.get_interaction_type_display()
        return f"{type_display} with {self.contact.name}"

    @property
    def is_scheduled(self):
        """Check if interaction is scheduled for the future."""
        if not self.scheduled_at:
            return False
        from django.utils import timezone
        return self.scheduled_at > timezone.now()

    @property
    def is_completed(self):
        """Check if interaction is completed."""
        return self.completed_at is not None

    @property
    def is_overdue(self):
        """Check if scheduled interaction is overdue."""
        if not self.scheduled_at or self.is_completed:
            return False
        from django.utils import timezone
        return self.scheduled_at < timezone.now()

    def mark_completed(self):
        """
        Mark interaction as completed.
        """
        from django.utils import timezone

        if not self.completed_at:
            self.completed_at = timezone.now()
            self.save(update_fields=['completed_at'])
