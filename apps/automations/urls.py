"""
Automations URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.automations.views import AutomationViewSet, WebhookViewSet

router = DefaultRouter()
router.register('automations', AutomationViewSet, basename='automation')
router.register('webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    path('', include(router.urls)),
]
