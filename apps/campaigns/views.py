"""
Campaigns views - ViewSets for Template, Campaign.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.campaigns.models import Template, Campaign
from apps.campaigns.serializers import (
    TemplateSerializer, TemplateListSerializer,
    CampaignSerializer, CampaignListSerializer, CampaignMetricsSerializer
)


class TemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for Template CRUD operations."""
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'content']
    filterset_fields = ['channel_type', 'is_active']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return TemplateListSerializer
        return TemplateSerializer

    def perform_create(self, serializer):
        """Auto-set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a template."""
        template = self.get_object()
        new_name = request.data.get('name')

        if not new_name:
            return Response(
                {'error': 'New name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_template = template.clone(new_name=new_name)
            serializer = self.get_serializer(new_template)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Render template with sample data."""
        template = self.get_object()
        sample_data = request.data.get('data', {})

        try:
            # Simple variable replacement (in production, use a template engine)
            rendered_content = template.content
            rendered_subject = template.subject

            for key, value in sample_data.items():
                placeholder = f"{{{{{key}}}}}"
                rendered_content = rendered_content.replace(placeholder, str(value))
                rendered_subject = rendered_subject.replace(placeholder, str(value))

            return Response({
                'subject': rendered_subject,
                'content': rendered_content,
                'variables_used': template.variables,
                'sample_data': sample_data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for Campaign CRUD operations."""
    queryset = Campaign.objects.select_related('template', 'channel').all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['campaign_type', 'status']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer

    def perform_create(self, serializer):
        """Auto-set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start campaign."""
        campaign = self.get_object()

        if campaign.start():
            return Response({
                'message': 'Campaign started successfully',
                'campaign': CampaignSerializer(campaign).data
            })
        else:
            return Response(
                {'error': f'Cannot start campaign with status {campaign.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause campaign."""
        campaign = self.get_object()

        if campaign.pause():
            return Response({
                'message': 'Campaign paused successfully',
                'campaign': CampaignSerializer(campaign).data
            })
        else:
            return Response(
                {'error': f'Cannot pause campaign with status {campaign.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel campaign."""
        campaign = self.get_object()

        if campaign.status in [Campaign.Status.DRAFT, Campaign.Status.SCHEDULED]:
            campaign.status = Campaign.Status.CANCELLED
            campaign.save(update_fields=['status'])
            return Response({
                'message': 'Campaign cancelled successfully',
                'campaign': CampaignSerializer(campaign).data
            })
        else:
            return Response(
                {'error': f'Cannot cancel campaign with status {campaign.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get detailed campaign metrics."""
        campaign = self.get_object()
        serializer = CampaignMetricsSerializer(campaign)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def test_send(self, request, pk=None):
        """Send campaign to test list."""
        campaign = self.get_object()
        test_emails = request.data.get('test_emails', [])

        if not test_emails:
            return Response(
                {'error': 'Test emails are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # In production, this would trigger actual email sending
        return Response({
            'message': f'Test campaign sent to {len(test_emails)} recipients',
            'recipients': test_emails,
            'template': campaign.template.name,
            'channel': campaign.channel.name
        })
