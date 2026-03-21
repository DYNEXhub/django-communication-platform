"""
Accounts views - ViewSets for User, Team, AuditLog.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from apps.accounts.models import User, Team, TeamMembership, AuditLog
from apps.accounts.serializers import (
    UserSerializer, UserCreateSerializer, UserListSerializer, UserProfileSerializer,
    ChangePasswordSerializer, TeamSerializer, TeamMembershipSerializer, AuditLogSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User CRUD operations."""
    queryset = User.objects.prefetch_related('teams').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    filterset_fields = ['role', 'is_active']

    def get_serializer_class(self):
        """Use appropriate serializer for each action."""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['me', 'update_profile']:
            return UserProfileSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update own profile."""
        user = request.user

        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            'message': 'Password changed successfully'
        })

    def update(self, request, *args, **kwargs):
        """Override update to restrict role changes to admins only."""
        user = self.get_object()

        # Only admins can change roles
        if 'role' in request.data and not request.user.is_admin:
            return Response(
                {'error': 'Only administrators can change user roles'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team CRUD operations."""
    queryset = Team.objects.prefetch_related('memberships__user').all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add user to team."""
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', TeamMembership.MemberRole.MEMBER)

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if membership already exists
        if TeamMembership.objects.filter(team=team, user=user).exists():
            return Response(
                {'error': 'User is already a member of this team'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create membership
        membership = TeamMembership.objects.create(
            team=team,
            user=user,
            role=role
        )

        serializer = TeamMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove user from team."""
        team = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            membership = TeamMembership.objects.get(team=team, user_id=user_id)
            membership.delete()
            return Response({
                'message': 'User removed from team successfully'
            })
        except TeamMembership.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this team'},
                status=status.HTTP_404_NOT_FOUND
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AuditLog (read-only, admin only)."""
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'action', 'entity_type']
