"""
Communications URLs - Router configuration for all communication-related endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.communications.views import (
    ChannelViewSet,
    EmailMessageViewSet,
    SMSMessageViewSet,
    WhatsAppMessageViewSet,
    ChatMessageViewSet,
)

app_name = 'communications'

router = DefaultRouter()
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'emails', EmailMessageViewSet, basename='email')
router.register(r'sms', SMSMessageViewSet, basename='sms')
router.register(r'whatsapp', WhatsAppMessageViewSet, basename='whatsapp')
router.register(r'chat', ChatMessageViewSet, basename='chat')

urlpatterns = [
    path('', include(router.urls)),
]
