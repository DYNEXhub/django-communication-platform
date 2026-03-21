"""
Contacts URLs - Router configuration for all contact-related endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.contacts.views import (
    TagViewSet,
    CompanyViewSet,
    ContactViewSet,
    ContactGroupViewSet,
    CustomFieldDefinitionViewSet,
    NoteViewSet,
)

app_name = 'contacts'

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'groups', ContactGroupViewSet, basename='group')
router.register(r'custom-fields', CustomFieldDefinitionViewSet, basename='customfield')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    path('', include(router.urls)),
]
