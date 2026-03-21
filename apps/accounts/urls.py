"""
Accounts URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.accounts.views import UserViewSet, TeamViewSet, AuditLogViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('teams', TeamViewSet, basename='team')
router.register('audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
]
