"""
Contacts filters - ContactFilter, CompanyFilter.
"""
import django_filters
from django.db.models import Q

from apps.contacts.models import Contact, Company


class ContactFilter(django_filters.FilterSet):
    """Filter for Contact model."""
    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=Contact.Status.choices
    )
    source = django_filters.ChoiceFilter(
        field_name='source',
        choices=Contact.Source.choices
    )
    company = django_filters.ModelChoiceFilter(
        queryset=Company.objects.all()
    )
    tags = django_filters.CharFilter(method='filter_tags')
    owner = django_filters.NumberFilter(field_name='owner_id')
    created_at = django_filters.DateFromToRangeFilter()
    has_phone = django_filters.BooleanFilter(method='filter_has_phone')

    class Meta:
        model = Contact
        fields = ['status', 'source', 'company', 'tags', 'owner', 'created_at', 'has_phone']

    def filter_tags(self, queryset, name, value):
        """Filter by tag name."""
        return queryset.filter(tags__name__icontains=value).distinct()

    def filter_has_phone(self, queryset, name, value):
        """Filter contacts with/without phone."""
        if value:
            return queryset.exclude(Q(phone='') | Q(phone__isnull=True))
        return queryset.filter(Q(phone='') | Q(phone__isnull=True))


class CompanyFilter(django_filters.FilterSet):
    """Filter for Company model."""
    industry = django_filters.CharFilter(lookup_expr='icontains')
    size = django_filters.ChoiceFilter(
        field_name='size',
        choices=Company.Size.choices
    )
    owner = django_filters.NumberFilter(field_name='owner_id')

    class Meta:
        model = Company
        fields = ['industry', 'size', 'owner']
