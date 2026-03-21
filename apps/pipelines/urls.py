"""
Pipelines URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.pipelines.views import (
    PipelineViewSet, PipelineStageViewSet, DealViewSet, InteractionViewSet
)

router = DefaultRouter()
router.register('pipelines', PipelineViewSet, basename='pipeline')
router.register('stages', PipelineStageViewSet, basename='pipeline-stage')
router.register('deals', DealViewSet, basename='deal')
router.register('interactions', InteractionViewSet, basename='interaction')

urlpatterns = [
    path('', include(router.urls)),
]
