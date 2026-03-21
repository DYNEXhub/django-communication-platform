"""
Contacts models - Company, Tag, Contact, ContactGroup, CustomFieldDefinition, Note.
"""
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class Company(BaseModel):
    """
    Company model for B2B contact management.
    """
    class Size(models.TextChoices):
        MICRO = 'MICRO', _('Micro (1-10)')
        SMALL = 'SMALL', _('Small (11-50)')
        MEDIUM = 'MEDIUM', _('Medium (51-200)')
        LARGE = 'LARGE', _('Large (201-1000)')
        ENTERPRISE = 'ENTERPRISE', _('Enterprise (1000+)')

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Company Name')
    )
    domain = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name=_('Domain')
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        verbose_name=_('Industry')
    )
    size = models.CharField(
        max_length=20,
        choices=Size.choices,
        blank=True,
        verbose_name=_('Company Size')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_companies',
        verbose_name=_('Owner')
    )

    class Meta:
        db_table = 'companies'
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
        ordering = ['name']
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['industry', 'size']),
        ]

    def __str__(self):
        return self.name

    @property
    def contact_count(self):
        """Return the number of contacts in this company."""
        return self.contacts.count()


class Tag(BaseModel):
    """
    Tag model for categorizing contacts, companies, and other entities.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_('Tag Name')
    )
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message=_('Color must be a valid hex color code (e.g., #6366f1)')
            )
        ],
        verbose_name=_('Color')
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        verbose_name=_('Category')
    )

    class Meta:
        db_table = 'tags'
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['category', 'name']

    def __str__(self):
        if self.category:
            return f"{self.category}: {self.name}"
        return self.name

    @property
    def usage_count(self):
        """Return the number of contacts using this tag."""
        return self.contacts.count()


class Contact(BaseModel):
    """
    Contact model - core entity for CRM and communication.
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        INACTIVE = 'INACTIVE', _('Inactive')
        UNSUBSCRIBED = 'UNSUBSCRIBED', _('Unsubscribed')

    class Source(models.TextChoices):
        MANUAL = 'MANUAL', _('Manual Entry')
        IMPORT = 'IMPORT', _('Import')
        API = 'API', _('API')
        FORM = 'FORM', _('Web Form')

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name=_('Full Name')
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name=_('Email Address')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone Number')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name=_('Status')
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.MANUAL,
        db_index=True,
        verbose_name=_('Source')
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contacts',
        verbose_name=_('Company')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='contacts',
        verbose_name=_('Tags')
    )
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Custom Fields')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_contacts',
        verbose_name=_('Owner')
    )

    class Meta:
        db_table = 'contacts'
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['owner', 'status']),
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    @property
    def is_active(self):
        """Check if contact is active."""
        return self.status == self.Status.ACTIVE

    @property
    def can_receive_messages(self):
        """Check if contact can receive messages."""
        return self.status != self.Status.UNSUBSCRIBED


class ContactGroup(BaseModel):
    """
    Contact group model for segmentation and bulk operations.
    Supports both static and dynamic (filter-based) groups.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Group Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    is_dynamic = models.BooleanField(
        default=False,
        verbose_name=_('Dynamic Group')
    )
    filter_criteria = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Filter Criteria')
    )
    contacts = models.ManyToManyField(
        Contact,
        blank=True,
        related_name='groups',
        verbose_name=_('Contacts')
    )

    class Meta:
        db_table = 'contact_groups'
        verbose_name = _('Contact Group')
        verbose_name_plural = _('Contact Groups')
        ordering = ['name']

    def __str__(self):
        group_type = 'Dynamic' if self.is_dynamic else 'Static'
        return f"{self.name} ({group_type})"

    @property
    def member_count(self):
        """Return the number of contacts in this group."""
        return self.contacts.count()

    def refresh_dynamic_members(self):
        """
        Refresh dynamic group members based on filter criteria.
        Only applicable for dynamic groups.
        """
        if not self.is_dynamic:
            return

        # This is a placeholder - actual implementation would depend on
        # the structure of filter_criteria
        # Example: self.contacts.set(Contact.objects.filter(**self.filter_criteria))
        pass


class CustomFieldDefinition(BaseModel):
    """
    Custom field definition for extending contact/company/deal data.
    """
    class FieldType(models.TextChoices):
        TEXT = 'TEXT', _('Text')
        NUMBER = 'NUMBER', _('Number')
        DATE = 'DATE', _('Date')
        DROPDOWN = 'DROPDOWN', _('Dropdown')
        BOOLEAN = 'BOOLEAN', _('Boolean')

    class EntityType(models.TextChoices):
        CONTACT = 'CONTACT', _('Contact')
        COMPANY = 'COMPANY', _('Company')
        DEAL = 'DEAL', _('Deal')

    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Field Name')
    )
    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        verbose_name=_('Field Type')
    )
    entity_type = models.CharField(
        max_length=20,
        choices=EntityType.choices,
        db_index=True,
        verbose_name=_('Entity Type')
    )
    options = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Options'),
        help_text=_('For dropdown fields, list of available options')
    )
    required = models.BooleanField(
        default=False,
        verbose_name=_('Required')
    )
    order = models.IntegerField(
        default=0,
        verbose_name=_('Display Order')
    )

    class Meta:
        db_table = 'custom_field_definitions'
        verbose_name = _('Custom Field Definition')
        verbose_name_plural = _('Custom Field Definitions')
        ordering = ['entity_type', 'order', 'name']
        unique_together = [['entity_type', 'name']]
        indexes = [
            models.Index(fields=['entity_type', 'order']),
        ]

    def __str__(self):
        return f"{self.get_entity_type_display()}.{self.name} ({self.get_field_type_display()})"

    @property
    def is_dropdown(self):
        """Check if this is a dropdown field."""
        return self.field_type == self.FieldType.DROPDOWN

    @property
    def has_options(self):
        """Check if options are defined."""
        return bool(self.options)


class Note(BaseModel):
    """
    Note model for adding comments to contacts.
    """
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Contact')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notes',
        verbose_name=_('Author')
    )
    content = models.TextField(
        verbose_name=_('Content')
    )
    pinned = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_('Pinned')
    )

    class Meta:
        db_table = 'contact_notes'
        verbose_name = _('Note')
        verbose_name_plural = _('Notes')
        ordering = ['-pinned', '-created_at']
        indexes = [
            models.Index(fields=['contact', '-pinned', '-created_at']),
        ]

    def __str__(self):
        author_name = self.author.get_full_name() if self.author else 'Unknown'
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"Note by {author_name}: {preview}"
