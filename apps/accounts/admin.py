"""
Django admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Team, TeamMembership, AuditLog


class TeamMembershipInline(admin.TabularInline):
    """Inline admin for team memberships."""
    model = TeamMembership
    extra = 0
    fields = ['user', 'role', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    list_display = ['username', 'email', 'role', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        (_('Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin configuration for Team model."""
    list_display = ['name', 'member_count', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    inlines = [TeamMembershipInline]

    def member_count(self, obj):
        """Display member count."""
        return obj.member_count
    member_count.short_description = 'Members'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""
    list_display = ['user', 'action', 'entity_type', 'entity_id', 'timestamp']
    list_filter = ['action', 'entity_type', 'timestamp']
    search_fields = ['entity_type', 'entity_id', 'user__username']
    ordering = ['-timestamp']
    readonly_fields = [
        'user', 'action', 'entity_type', 'entity_id',
        'changes', 'ip_address', 'timestamp'
    ]

    def has_add_permission(self, request):
        """Disable manual creation of audit logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deletion of audit logs."""
        return False
