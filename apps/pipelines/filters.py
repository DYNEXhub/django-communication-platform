"""
Pipelines filters for django-filter integration.
"""
from django_filters import rest_framework as filters
from apps.pipelines.models import Deal, Interaction


class DealFilter(filters.FilterSet):
    """Filter for Deal model."""
    status = filters.ChoiceFilter(choices=Deal.Status.choices)
    stage = filters.NumberFilter(field_name='stage__id')
    pipeline = filters.NumberFilter(field_name='stage__pipeline__id')
    contact = filters.NumberFilter(field_name='contact__id')
    owner = filters.UUIDFilter(field_name='owner__id')
    expected_close_date = filters.DateFromToRangeFilter()
    value = filters.RangeFilter()
    created_at = filters.DateFromToRangeFilter()

    class Meta:
        model = Deal
        fields = [
            'status', 'stage', 'pipeline', 'contact', 'owner',
            'expected_close_date', 'value', 'created_at'
        ]


class InteractionFilter(filters.FilterSet):
    """Filter for Interaction model."""
    contact = filters.NumberFilter(field_name='contact__id')
    deal = filters.NumberFilter(field_name='deal__id')
    interaction_type = filters.ChoiceFilter(choices=Interaction.InteractionType.choices)
    agent = filters.UUIDFilter(field_name='agent__id')
    scheduled_at = filters.DateFromToRangeFilter()
    is_completed = filters.BooleanFilter(method='filter_is_completed')

    class Meta:
        model = Interaction
        fields = [
            'contact', 'deal', 'interaction_type', 'agent',
            'scheduled_at', 'is_completed'
        ]

    def filter_is_completed(self, queryset, name, value):
        """Filter by completion status."""
        if value is True:
            return queryset.exclude(completed_at__isnull=True)
        elif value is False:
            return queryset.filter(completed_at__isnull=True)
        return queryset
