"""
Pipelines serializers.
"""
from rest_framework import serializers
from apps.pipelines.models import Pipeline, PipelineStage, Deal, Interaction
from apps.contacts.models import Contact
from apps.accounts.models import User


class PipelineStageSerializer(serializers.ModelSerializer):
    """Full serializer for PipelineStage."""
    deal_count = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = PipelineStage
        fields = [
            'id', 'pipeline', 'name', 'order', 'probability', 'color',
            'deal_count', 'total_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deal_count', 'total_value']


class PipelineSerializer(serializers.ModelSerializer):
    """Full serializer for Pipeline with nested stages."""
    stages = PipelineStageSerializer(many=True, read_only=True)
    stage_count = serializers.IntegerField(read_only=True)
    deal_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pipeline
        fields = [
            'id', 'name', 'description', 'is_default', 'created_by',
            'stages', 'stage_count', 'deal_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'stage_count', 'deal_count']


class PipelineListSerializer(serializers.ModelSerializer):
    """List serializer for Pipeline."""
    stage_count = serializers.IntegerField(read_only=True)
    deal_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pipeline
        fields = [
            'id', 'name', 'is_default', 'stage_count', 'deal_count', 'created_at'
        ]
        read_only_fields = ['id', 'stage_count', 'deal_count', 'created_at']


class DealSerializer(serializers.ModelSerializer):
    """Full serializer for Deal with nested contact, stage, owner."""
    weighted_value = serializers.FloatField(read_only=True)
    days_in_stage = serializers.IntegerField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)

    # Nested read representations
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    contact_email = serializers.EmailField(source='contact.email', read_only=True)
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    pipeline_name = serializers.CharField(source='stage.pipeline.name', read_only=True)
    owner_id = serializers.UUIDField(source='owner.id', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

    # Write fields
    stage_id = serializers.PrimaryKeyRelatedField(
        queryset=PipelineStage.objects.all(),
        source='stage',
        write_only=True,
        required=False
    )
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        source='contact',
        write_only=True,
        required=False
    )
    owner_id_write = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='owner',
        write_only=True,
        required=False
    )

    class Meta:
        model = Deal
        fields = [
            'id', 'name', 'value', 'stage', 'contact', 'owner', 'status',
            'probability', 'expected_close_date', 'closed_at', 'lost_reason',
            'weighted_value', 'days_in_stage', 'is_open',
            'contact_name', 'contact_email', 'stage_name', 'pipeline_name',
            'owner_id', 'owner_username',
            'stage_id', 'contact_id', 'owner_id_write',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'weighted_value',
            'days_in_stage', 'is_open', 'contact_name', 'contact_email',
            'stage_name', 'pipeline_name', 'owner_id', 'owner_username'
        ]


class DealListSerializer(serializers.ModelSerializer):
    """List serializer for Deal."""
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Deal
        fields = [
            'id', 'name', 'value', 'status', 'stage_name', 'contact_name',
            'owner_name', 'expected_close_date', 'created_at'
        ]
        read_only_fields = [
            'id', 'stage_name', 'contact_name', 'owner_name', 'created_at'
        ]


class DealMoveSerializer(serializers.Serializer):
    """Serializer for moving deals between stages."""
    stage_id = serializers.PrimaryKeyRelatedField(
        queryset=PipelineStage.objects.all(),
        required=True
    )


class InteractionSerializer(serializers.ModelSerializer):
    """Full serializer for Interaction."""
    is_completed = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    # Nested read representations
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    agent_username = serializers.CharField(source='agent.username', read_only=True)

    # Write fields
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        source='contact',
        write_only=True,
        required=False
    )
    deal_id = serializers.PrimaryKeyRelatedField(
        queryset=Deal.objects.all(),
        source='deal',
        write_only=True,
        required=False
    )
    agent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='agent',
        write_only=True,
        required=False
    )

    class Meta:
        model = Interaction
        fields = [
            'id', 'contact', 'deal', 'interaction_type', 'notes', 'agent',
            'scheduled_at', 'completed_at', 'is_completed', 'is_overdue',
            'contact_name', 'agent_username',
            'contact_id', 'deal_id', 'agent_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'is_completed', 'is_overdue',
            'contact_name', 'agent_username'
        ]


class InteractionListSerializer(serializers.ModelSerializer):
    """List serializer for Interaction."""
    contact_name = serializers.CharField(source='contact.name', read_only=True)
    deal_name = serializers.CharField(source='deal.name', read_only=True)
    agent_name = serializers.CharField(source='agent.username', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Interaction
        fields = [
            'id', 'interaction_type', 'contact_name', 'deal_name', 'agent_name',
            'scheduled_at', 'completed_at', 'is_overdue'
        ]
        read_only_fields = [
            'id', 'contact_name', 'deal_name', 'agent_name', 'is_overdue'
        ]
