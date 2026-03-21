"""
Campaigns serializers.
"""
from rest_framework import serializers
from apps.campaigns.models import Template, Campaign
from apps.communications.models import Channel
from apps.contacts.models import ContactGroup


class TemplateSerializer(serializers.ModelSerializer):
    """Full serializer for Template."""

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'channel_type', 'subject', 'content', 'variables',
            'version', 'is_active', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'version', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        """Auto-increment version on update."""
        instance.version += 1
        return super().update(instance, validated_data)


class TemplateListSerializer(serializers.ModelSerializer):
    """List serializer for Template."""

    class Meta:
        model = Template
        fields = [
            'id', 'name', 'channel_type', 'is_active', 'version', 'created_at'
        ]
        read_only_fields = ['id', 'version', 'created_at']


class CampaignSerializer(serializers.ModelSerializer):
    """Full serializer for Campaign."""
    # Read-only computed fields
    total_recipients = serializers.IntegerField(read_only=True)
    sent_count = serializers.IntegerField(read_only=True)
    open_count = serializers.IntegerField(read_only=True)
    click_count = serializers.IntegerField(read_only=True)
    bounce_count = serializers.IntegerField(read_only=True)
    started_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True)

    # Nested read representations
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_channel = serializers.CharField(source='template.channel_type', read_only=True)
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    channel_type = serializers.CharField(source='channel.channel_type', read_only=True)

    # Write fields
    template_id = serializers.PrimaryKeyRelatedField(
        queryset=Template.objects.all(),
        source='template',
        write_only=True,
        required=False
    )
    channel_id = serializers.PrimaryKeyRelatedField(
        queryset=Channel.objects.all(),
        source='channel',
        write_only=True,
        required=False
    )
    segment_ids = serializers.PrimaryKeyRelatedField(
        queryset=ContactGroup.objects.all(),
        source='segments',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'campaign_type', 'template', 'channel', 'segments',
            'status', 'scheduled_at', 'started_at', 'completed_at',
            'total_recipients', 'sent_count', 'open_count', 'click_count',
            'bounce_count', 'created_by',
            'template_name', 'template_channel', 'channel_name', 'channel_type',
            'template_id', 'channel_id', 'segment_ids',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'started_at', 'completed_at', 'total_recipients',
            'sent_count', 'open_count', 'click_count', 'bounce_count',
            'template_name', 'template_channel', 'channel_name', 'channel_type',
            'created_at', 'updated_at'
        ]



class CampaignListSerializer(serializers.ModelSerializer):
    """List serializer for Campaign."""

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'campaign_type', 'status', 'total_recipients',
            'sent_count', 'open_count', 'scheduled_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'total_recipients', 'sent_count', 'open_count', 'created_at'
        ]


class CampaignMetricsSerializer(serializers.ModelSerializer):
    """Serializer for campaign metrics with calculated rates."""
    open_rate = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()
    bounce_rate = serializers.SerializerMethodField()
    delivery_rate = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'total_recipients', 'sent_count', 'open_count', 'click_count',
            'bounce_count', 'open_rate', 'click_rate', 'bounce_rate', 'delivery_rate'
        ]
        read_only_fields = [
            'total_recipients', 'sent_count', 'open_count', 'click_count',
            'bounce_count'
        ]

    def get_open_rate(self, obj):
        """Calculate open rate percentage."""
        return round(obj.open_rate, 2)

    def get_click_rate(self, obj):
        """Calculate click rate percentage."""
        return round(obj.click_rate, 2)

    def get_bounce_rate(self, obj):
        """Calculate bounce rate percentage."""
        return round(obj.bounce_rate, 2)

    def get_delivery_rate(self, obj):
        """Calculate delivery rate percentage."""
        return round(obj.delivery_rate, 2)
