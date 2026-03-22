"""
Dashboard stats endpoint — aggregates data from contacts, pipelines, campaigns.
"""
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.contacts.models import Contact
from apps.pipelines.models import Deal, PipelineStage
from apps.campaigns.models import Campaign


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """GET /api/v1/dashboard/stats/ — aggregate dashboard metrics."""
    total_contacts = Contact.objects.count()
    active_deals = Deal.objects.filter(status=Deal.Status.OPEN).count()
    total_deal_value = Deal.objects.filter(
        status=Deal.Status.OPEN
    ).aggregate(total=Sum('value'))['total'] or 0

    campaigns_sent = Campaign.objects.filter(
        status__in=[Campaign.Status.COMPLETED, Campaign.Status.RUNNING]
    ).count()

    # Average open rate across completed campaigns
    completed_campaigns = Campaign.objects.filter(status=Campaign.Status.COMPLETED)
    if completed_campaigns.exists():
        total_sent = sum(c.sent_count for c in completed_campaigns if c.sent_count > 0)
        total_opened = sum(c.open_count for c in completed_campaigns)
        open_rate = round((total_opened / total_sent) * 100, 1) if total_sent > 0 else 0
    else:
        open_rate = 0

    # Pipeline by stage (for bar chart)
    pipeline_by_stage = list(
        PipelineStage.objects.annotate(
            deal_count=Count('deals', filter=Q(deals__status=Deal.Status.OPEN)),
            total_value=Sum('deals__value', filter=Q(deals__status=Deal.Status.OPEN)),
        ).values('name', 'color', 'order', 'deal_count', 'total_value')
        .order_by('order')
    )
    # Convert Decimal to float for JSON
    for stage in pipeline_by_stage:
        stage['total_value'] = float(stage['total_value'] or 0)

    # Contacts by month (for line chart — last 6 months)
    contacts_by_month = list(
        Contact.objects.annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    # Format dates for JSON
    for entry in contacts_by_month:
        entry['month'] = entry['month'].strftime('%Y-%m')

    return Response({
        'total_contacts': total_contacts,
        'active_deals': active_deals,
        'total_deal_value': float(total_deal_value),
        'campaigns_sent': campaigns_sent,
        'open_rate': open_rate,
        'pipeline_by_stage': pipeline_by_stage,
        'contacts_by_month': contacts_by_month,
    })
