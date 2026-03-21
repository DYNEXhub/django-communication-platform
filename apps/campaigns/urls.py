"""
Campaigns URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.campaigns.views import TemplateViewSet, CampaignViewSet

router = DefaultRouter()
router.register('templates', TemplateViewSet, basename='template')
router.register('campaigns', CampaignViewSet, basename='campaign')

urlpatterns = [
    path('', include(router.urls)),
]
