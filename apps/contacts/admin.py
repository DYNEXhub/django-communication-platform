"""
Django admin configuration for contacts app.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import Company, Tag, Contact, ContactGroup, CustomFieldDefinition, Note


class NoteInline(admin.StackedInline):
    """Inline admin for contact notes."""
    model = Note
    extra = 0
    fields = ['author', 'content', 'pinned', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin configuration for Company model."""
    list_display = ['name', 'domain', 'industry', 'size', 'contact_count', 'created_at']
    list_filter = ['industry', 'size']
    search_fields = ['name', 'domain']
    ordering = ['name']

    def contact_count(self, obj):
        """Display contact count."""
        return obj.contact_count
    contact_count.short_description = 'Contacts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model."""
    list_display = ['name', 'color_badge', 'category', 'usage_count']
    list_filter = ['category']
    search_fields = ['name', 'category']
    ordering = ['category', 'name']

    def color_badge(self, obj):
        """Display color as a visual badge."""
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; color: white; border-radius: 3px;">{}</span>',
            obj.color,
            obj.color
        )
    color_badge.short_description = 'Color'

    def usage_count(self, obj):
        """Display usage count."""
        return obj.usage_count
    usage_count.short_description = 'Used by'


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin configuration for Contact model."""
    list_display = ['name', 'email', 'phone', 'status', 'source', 'company', 'created_at']
    list_filter = ['status', 'source', 'company']
    search_fields = ['name', 'email', 'phone']
    filter_horizontal = ['tags']
    ordering = ['-created_at']
    inlines = [NoteInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'status', 'source')
        }),
        ('Organization', {
            'fields': ('company', 'owner')
        }),
        ('Categorization', {
            'fields': ('tags',)
        }),
        ('Custom Fields', {
            'fields': ('custom_fields',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    """Admin configuration for ContactGroup model."""
    list_display = ['name', 'is_dynamic', 'member_count', 'created_at']
    list_filter = ['is_dynamic']
    search_fields = ['name', 'description']
    filter_horizontal = ['contacts']
    ordering = ['name']

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_dynamic')
        }),
        ('Dynamic Criteria', {
            'fields': ('filter_criteria',),
            'classes': ('collapse',)
        }),
        ('Members', {
            'fields': ('contacts',)
        }),
    )

    def member_count(self, obj):
        """Display member count."""
        return obj.member_count
    member_count.short_description = 'Members'


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    """Admin configuration for CustomFieldDefinition model."""
    list_display = ['name', 'field_type', 'entity_type', 'required', 'order']
    list_filter = ['field_type', 'entity_type', 'required']
    search_fields = ['name']
    ordering = ['entity_type', 'order', 'name']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Admin configuration for Note model."""
    list_display = ['contact', 'author', 'pinned', 'content_preview', 'created_at']
    list_filter = ['pinned', 'author']
    search_fields = ['content', 'contact__name']
    ordering = ['-pinned', '-created_at']

    def content_preview(self, obj):
        """Display content preview."""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return preview
    content_preview.short_description = 'Content'
