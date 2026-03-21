"""
Automations views - ViewSets for Automation, Webhook.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.automations.models import Automation, AutomationLog, Webhook, WebhookDelivery
from apps.automations.serializers import (
    AutomationSerializer, AutomationListSerializer, AutomationLogSerializer,
    WebhookSerializer, WebhookDeliverySerializer
)


class AutomationViewSet(viewsets.ModelViewSet):
    """ViewSet for Automation CRUD operations."""
    queryset = Automation.objects.all()
    serializer_class = AutomationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['trigger_type', 'is_active']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return AutomationListSerializer
        return AutomationSerializer

    def perform_create(self, serializer):
        """Auto-set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate automation."""
        automation = self.get_object()
        automation.is_active = True
        automation.save(update_fields=['is_active'])

        return Response({
            'message': 'Automation activated successfully',
            'automation': AutomationSerializer(automation).data
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate automation."""
        automation = self.get_object()
        automation.is_active = False
        automation.save(update_fields=['is_active'])

        return Response({
            'message': 'Automation deactivated successfully',
            'automation': AutomationSerializer(automation).data
        })

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test run automation with sample data."""
        automation = self.get_object()
        sample_data = request.data.get('data', {})

        try:
            # Execute automation with sample data
            log = automation.execute(trigger_data=sample_data)

            return Response({
                'message': 'Automation test executed successfully',
                'log': AutomationLogSerializer(log).data if log else None,
                'automation': AutomationSerializer(automation).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """List execution logs for this automation."""
        automation = self.get_object()
        logs = automation.logs.all()[:50]  # Latest 50 logs
        serializer = AutomationLogSerializer(logs, many=True)
        return Response(serializer.data)


class WebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for Webhook CRUD operations."""
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

    def perform_create(self, serializer):
        """Auto-set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send test webhook."""
        webhook = self.get_object()
        test_event = request.data.get('event', 'test_event')
        test_payload = request.data.get('payload', {'test': True})

        if test_event not in webhook.events:
            return Response(
                {'error': f'Event "{test_event}" is not in webhook events list'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Send webhook (in production, this would make actual HTTP request)
            delivery = webhook.send(event=test_event, payload=test_payload)

            return Response({
                'message': 'Test webhook sent successfully',
                'delivery': WebhookDeliverySerializer(delivery).data if delivery else None
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def deliveries(self, request, pk=None):
        """List delivery attempts for this webhook."""
        webhook = self.get_object()
        deliveries = webhook.deliveries.all()[:50]  # Latest 50 deliveries
        serializer = WebhookDeliverySerializer(deliveries, many=True)
        return Response(serializer.data)
