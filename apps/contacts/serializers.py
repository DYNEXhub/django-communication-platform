"""
Contacts serializers - Tag, Company, Contact, ContactGroup, CustomFieldDefinition, Note.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.contacts.models import (
    Tag,
    Company,
    Contact,
    ContactGroup,
    CustomFieldDefinition,
    Note,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Tag serializer with usage count."""
    usage_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'category', 'created_at', 'usage_count']
        read_only_fields = ['id', 'created_at', 'usage_count']


class SimpleUserSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested representation."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CompanyListSerializer(serializers.ModelSerializer):
    """Simplified company serializer for list views."""
    contact_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'name', 'domain', 'industry', 'size', 'contact_count']


class CompanySerializer(serializers.ModelSerializer):
    """Full company serializer with owner details."""
    contact_count = serializers.IntegerField(read_only=True)
    owner = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'domain', 'industry', 'size', 'owner',
            'contact_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'contact_count']


class ContactListSerializer(serializers.ModelSerializer):
    """Simplified contact serializer for list views."""
    company = serializers.SerializerMethodField()
    tag_count = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'name', 'email', 'phone', 'status', 'source',
            'company', 'tag_count', 'created_at'
        ]

    def get_company(self, obj):
        """Return company name only."""
        return obj.company.name if obj.company else None

    def get_tag_count(self, obj):
        """Return number of tags."""
        return obj.tags.count()


class ContactSerializer(serializers.ModelSerializer):
    """Full contact serializer with nested relationships."""
    company = CompanyListSerializer(read_only=True)
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company',
        write_only=True,
        required=False,
        allow_null=True
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = [
            'id', 'name', 'email', 'phone', 'status', 'source',
            'company', 'company_id', 'tags', 'tag_ids', 'custom_fields',
            'owner', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']

    def get_full_name(self, obj):
        """Return full name with email."""
        return f"{obj.name} <{obj.email}>"

    def create(self, validated_data):
        """Handle M2M tags on creation."""
        tags = validated_data.pop('tags', [])
        contact = Contact.objects.create(**validated_data)
        if tags:
            contact.tags.set(tags)
        return contact

    def update(self, instance, validated_data):
        """Handle M2M tags on update."""
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        return instance


class ContactGroupSerializer(serializers.ModelSerializer):
    """Contact group serializer with member count."""
    member_count = serializers.IntegerField(read_only=True)
    contact_ids = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        source='contacts',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = ContactGroup
        fields = [
            'id', 'name', 'description', 'is_dynamic', 'filter_criteria',
            'contacts', 'contact_ids', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_count']

    def create(self, validated_data):
        """Handle M2M contacts on creation (static groups only)."""
        contacts = validated_data.pop('contacts', [])
        group = ContactGroup.objects.create(**validated_data)
        if not group.is_dynamic and contacts:
            group.contacts.set(contacts)
        return group

    def update(self, instance, validated_data):
        """Handle M2M contacts on update."""
        contacts = validated_data.pop('contacts', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contacts is not None and not instance.is_dynamic:
            instance.contacts.set(contacts)

        return instance


class CustomFieldDefinitionSerializer(serializers.ModelSerializer):
    """Custom field definition serializer."""
    class Meta:
        model = CustomFieldDefinition
        fields = [
            'id', 'name', 'field_type', 'entity_type', 'options',
            'required', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NoteSerializer(serializers.ModelSerializer):
    """Note serializer with author details."""
    author = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = [
            'id', 'contact', 'author', 'content', 'pinned',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class ContactImportSerializer(serializers.Serializer):
    """Serializer for CSV contact import."""
    file = serializers.FileField()
    has_header = serializers.BooleanField(default=True)
