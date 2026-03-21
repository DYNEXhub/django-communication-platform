"""
Communications filters - EmailMessageFilter, SMSMessageFilter.
"""
import django_filters

from apps.communications.models import EmailMessage, SMSMessage


class EmailMessageFilter(django_filters.FilterSet):
    """Filter for EmailMessage model."""
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=EmailMessage.Status.choices
    )
    opened = django_filters.BooleanFilter()
    clicked = django_filters.BooleanFilter()
    contact = django_filters.NumberFilter(field_name='contact_id')
    channel = django_filters.NumberFilter(field_name='channel_id')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = EmailMessage
        fields = ['status', 'opened', 'clicked', 'contact', 'channel', 'created_at']


class SMSMessageFilter(django_filters.FilterSet):
    """Filter for SMSMessage model."""
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=SMSMessage.Status.choices
    )
    contact = django_filters.NumberFilter(field_name='contact_id')

    class Meta:
        model = SMSMessage
        fields = ['status', 'contact']
