"""
Accounts models - User, Team, TeamMembership, AuditLog.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with UUID primary key.
    Supports role-based access control and team membership.
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        MANAGER = 'MANAGER', _('Manager')
        AGENT = 'AGENT', _('Agent')
        VIEWER = 'VIEWER', _('Viewer')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.AGENT,
        db_index=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Phone Number')
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Avatar')
    )
    teams = models.ManyToManyField(
        'Team',
        through='TeamMembership',
        related_name='team_members',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN

    @property
    def is_manager(self):
        """Check if user has manager or admin role."""
        return self.role in [self.Role.ADMIN, self.Role.MANAGER]


class Team(BaseModel):
    """
    Team model for organizing users into groups.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Team Name')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )

    class Meta:
        db_table = 'teams'
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Return the number of members in this team."""
        return self.memberships.count()

    @property
    def leaders(self):
        """Return all team leaders."""
        return User.objects.filter(
            team_memberships__team=self,
            team_memberships__role=TeamMembership.MemberRole.LEADER
        )


class TeamMembership(models.Model):
    """
    Through model for User-Team relationship with role.
    """
    class MemberRole(models.TextChoices):
        LEADER = 'LEADER', _('Team Leader')
        MEMBER = 'MEMBER', _('Team Member')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=MemberRole.choices,
        default=MemberRole.MEMBER,
        verbose_name=_('Role')
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Joined At')
    )

    class Meta:
        db_table = 'team_memberships'
        verbose_name = _('Team Membership')
        verbose_name_plural = _('Team Memberships')
        unique_together = [['user', 'team']]
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['team', 'role']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} in {self.team.name} ({self.get_role_display()})"

    @property
    def is_leader(self):
        """Check if this membership is a leadership role."""
        return self.role == self.MemberRole.LEADER


class AuditLog(BaseModel):
    """
    Audit log for tracking all system changes.
    """
    class Action(models.TextChoices):
        CREATE = 'CREATE', _('Create')
        UPDATE = 'UPDATE', _('Update')
        DELETE = 'DELETE', _('Delete')
        LOGIN = 'LOGIN', _('Login')
        LOGOUT = 'LOGOUT', _('Logout')
        VIEW = 'VIEW', _('View')

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name=_('User')
    )
    action = models.CharField(
        max_length=50,
        choices=Action.choices,
        db_index=True,
        verbose_name=_('Action')
    )
    entity_type = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_('Entity Type')
    )
    entity_id = models.UUIDField(
        db_index=True,
        verbose_name=_('Entity ID')
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Changes')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Address')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Timestamp')
    )

    class Meta:
        db_table = 'audit_logs'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else 'System'
        return f"{user_str} {self.action} {self.entity_type} at {self.timestamp}"

    @property
    def has_changes(self):
        """Check if this log has any recorded changes."""
        return bool(self.changes)
