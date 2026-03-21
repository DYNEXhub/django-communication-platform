"""
Django admin configuration for pipelines app.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Pipeline, PipelineStage, Deal, Interaction


class PipelineStageInline(admin.TabularInline):
    """Inline admin for pipeline stages."""
    model = PipelineStage
    extra = 1
    fields = ['name', 'order', 'probability', 'color']
    ordering = ['order']


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    """Admin configuration for Pipeline model."""
    list_display = ['name', 'is_default', 'stage_count', 'deal_count', 'created_at']
    list_filter = ['is_default']
    search_fields = ['name', 'description']
    ordering = ['-is_default', 'name']
    inlines = [PipelineStageInline]

    def stage_count(self, obj):
        """Display stage count."""
        return obj.stage_count
    stage_count.short_description = 'Stages'

    def deal_count(self, obj):
        """Display deal count."""
        return obj.deal_count
    deal_count.short_description = 'Deals'


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    """Admin configuration for PipelineStage model."""
    list_display = ['pipeline', 'name', 'order', 'probability', 'deal_count', 'color_badge']
    list_filter = ['pipeline']
    search_fields = ['name', 'pipeline__name']
    ordering = ['pipeline', 'order']

    def color_badge(self, obj):
        """Display color as a visual badge."""
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_badge.short_description = 'Color'

    def deal_count(self, obj):
        """Display deal count."""
        return obj.deal_count
    deal_count.short_description = 'Deals'


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    """Admin configuration for Deal model."""
    list_display = [
        'name', 'value', 'stage', 'contact', 'owner',
        'status', 'probability', 'expected_close_date'
    ]
    list_filter = ['status', 'stage__pipeline', 'owner']
    search_fields = ['name', 'contact__name', 'contact__email']
    ordering = ['-created_at']
    readonly_fields = ['closed_at', 'weighted_value_display', 'days_in_stage_display']

    fieldsets = (
        (None, {
            'fields': ('name', 'value', 'stage', 'contact', 'owner')
        }),
        ('Status', {
            'fields': ('status', 'probability', 'expected_close_date', 'closed_at')
        }),
        ('Loss Details', {
            'fields': ('lost_reason',),
            'classes': ('collapse',)
        }),
        ('Computed Values', {
            'fields': ('weighted_value_display', 'days_in_stage_display'),
            'classes': ('collapse',)
        }),
    )

    def weighted_value_display(self, obj):
        """Display weighted value."""
        return format_html('<strong>${:,.2f}</strong>', obj.weighted_value)
    weighted_value_display.short_description = 'Weighted Value'

    def days_in_stage_display(self, obj):
        """Display days in current stage."""
        return format_html('<strong>{} days</strong>', obj.days_in_stage)
    days_in_stage_display.short_description = 'Days in Stage'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    """Admin configuration for Interaction model."""
    list_display = [
        'contact', 'deal', 'interaction_type',
        'agent', 'scheduled_at', 'completed_at'
    ]
    list_filter = ['interaction_type', 'agent']
    search_fields = ['contact__name', 'notes']
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('contact', 'deal', 'interaction_type', 'agent')
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'completed_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
