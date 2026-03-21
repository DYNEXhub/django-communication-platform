"""
Accounts serializers.
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from apps.accounts.models import User, Team, TeamMembership, AuditLog


class TeamMembershipSerializer(serializers.ModelSerializer):
    """Serializer for TeamMembership."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = TeamMembership
        fields = ['id', 'user', 'team', 'role', 'joined_at', 'user_username', 'team_name']
        read_only_fields = ['id', 'joined_at', 'user_username', 'team_name']


class TeamSerializer(serializers.ModelSerializer):
    """Full serializer for Team with nested members."""
    member_count = serializers.IntegerField(read_only=True)
    members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'member_count', 'members',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'member_count', 'created_at', 'updated_at']

    def get_members(self, obj):
        """Get list of team members with user_id, username, role."""
        memberships = obj.memberships.select_related('user').all()
        return [
            {
                'user_id': str(membership.user.id),
                'username': membership.user.username,
                'role': membership.role
            }
            for membership in memberships
        ]


class UserSerializer(serializers.ModelSerializer):
    """Full serializer for User."""
    teams = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone', 'avatar', 'is_active', 'date_joined', 'last_login', 'teams'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'teams']

    def get_teams(self, obj):
        """Get list of teams with id and name."""
        return [
            {'id': str(team.id), 'name': team.name}
            for team in obj.teams.all()
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user creation with password."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone'
        ]

    def create(self, validated_data):
        """Create user with hashed password."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', User.Role.AGENT),
            phone=validated_data.get('phone', '')
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    """List serializer for User."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'role', 'is_active']
        read_only_fields = ['id', 'full_name']

    def get_full_name(self, obj):
        """Get user's full name."""
        return obj.get_full_name() or obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile updates (self-service)."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'avatar', 'role']
        read_only_fields = ['id', 'username', 'email', 'role']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match'
            })
        return attrs

    def validate_old_password(self, value):
        """Validate old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog (read-only)."""
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_username', 'action', 'entity_type', 'entity_id',
            'changes', 'ip_address', 'timestamp'
        ]
        read_only_fields = [
            'id', 'user', 'user_username', 'action', 'entity_type', 'entity_id',
            'changes', 'ip_address', 'timestamp'
        ]
