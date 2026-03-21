"""
Pipelines views - ViewSets for Pipeline, PipelineStage, Deal, Interaction.
"""
from django.db import models
from django.db.models import Count, Sum, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.pipelines.models import Pipeline, PipelineStage, Deal, Interaction
from apps.pipelines.serializers import (
    PipelineSerializer, PipelineListSerializer, PipelineStageSerializer,
    DealSerializer, DealListSerializer, DealMoveSerializer,
    InteractionSerializer, InteractionListSerializer
)
from apps.pipelines.filters import DealFilter, InteractionFilter


class PipelineViewSet(viewsets.ModelViewSet):
    """ViewSet for Pipeline CRUD operations."""
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return PipelineListSerializer
        return PipelineSerializer

    def perform_create(self, serializer):
        """Auto-set created_by to current user."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def stages(self, request, pk=None):
        """List all stages for this pipeline."""
        pipeline = self.get_object()
        stages = pipeline.stages.all()
        serializer = PipelineStageSerializer(stages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def deals(self, request, pk=None):
        """List all deals in this pipeline."""
        pipeline = self.get_object()
        deals = Deal.objects.filter(stage__pipeline=pipeline)
        serializer = DealListSerializer(deals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get pipeline statistics."""
        pipeline = self.get_object()

        # Total value across all stages
        total_value = Deal.objects.filter(
            stage__pipeline=pipeline,
            status=Deal.Status.OPEN
        ).aggregate(total=Sum('value'))['total'] or 0

        # Deal count by stage
        deals_by_stage = pipeline.stages.annotate(
            deal_count=Count('deals', filter=Q(deals__status=Deal.Status.OPEN))
        ).values('id', 'name', 'deal_count', 'probability')

        # Win rate
        total_closed = Deal.objects.filter(stage__pipeline=pipeline).exclude(
            status=Deal.Status.OPEN
        ).count()
        total_won = Deal.objects.filter(
            stage__pipeline=pipeline,
            status=Deal.Status.WON
        ).count()
        win_rate = (total_won / total_closed * 100) if total_closed > 0 else 0

        return Response({
            'total_value': total_value,
            'deals_by_stage': list(deals_by_stage),
            'win_rate': round(win_rate, 2),
            'total_closed_deals': total_closed,
            'total_won_deals': total_won
        })


class PipelineStageViewSet(viewsets.ModelViewSet):
    """ViewSet for PipelineStage CRUD operations."""
    queryset = PipelineStage.objects.all()
    serializer_class = PipelineStageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pipeline']

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Change stage order."""
        stage = self.get_object()
        new_order = request.data.get('order')

        if new_order is None:
            return Response(
                {'error': 'Order is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_order = int(new_order)
            if new_order < 0:
                raise ValueError("Order must be >= 0")
        except (ValueError, TypeError) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        stage.order = new_order
        stage.save(update_fields=['order'])

        serializer = self.get_serializer(stage)
        return Response(serializer.data)


class DealViewSet(viewsets.ModelViewSet):
    """ViewSet for Deal CRUD operations."""
    queryset = Deal.objects.select_related('stage', 'contact', 'owner').all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name']
    filterset_class = DealFilter
    ordering_fields = ['value', 'created_at', 'expected_close_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return DealListSerializer
        return DealSerializer

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Move deal to another stage."""
        deal = self.get_object()
        serializer = DealMoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_stage = serializer.validated_data['stage_id']

        try:
            deal.move_to_stage(new_stage)
            return Response({
                'message': f'Deal moved to {new_stage.name}',
                'stage': PipelineStageSerializer(new_stage).data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def mark_won(self, request, pk=None):
        """Mark deal as won."""
        deal = self.get_object()
        deal.mark_won()
        serializer = self.get_serializer(deal)
        return Response({
            'message': 'Deal marked as won',
            'deal': serializer.data
        })

    @action(detail=True, methods=['post'])
    def mark_lost(self, request, pk=None):
        """Mark deal as lost."""
        deal = self.get_object()
        reason = request.data.get('reason', '')
        deal.mark_lost(reason=reason)
        serializer = self.get_serializer(deal)
        return Response({
            'message': 'Deal marked as lost',
            'deal': serializer.data
        })


class InteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for Interaction CRUD operations."""
    queryset = Interaction.objects.select_related('contact', 'deal', 'agent').all()
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = InteractionFilter

    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return InteractionListSerializer
        return InteractionSerializer

    def perform_create(self, serializer):
        """Auto-set agent to current user if not provided."""
        if not serializer.validated_data.get('agent'):
            serializer.save(agent=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark interaction as completed."""
        interaction = self.get_object()
        interaction.mark_completed()
        serializer = self.get_serializer(interaction)
        return Response({
            'message': 'Interaction marked as completed',
            'interaction': serializer.data
        })
