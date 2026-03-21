"""
URL configuration for Django Communication Platform.
Main routing for API endpoints and admin panel.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # Authentication endpoints
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API v1 endpoints
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/contacts/', include('apps.contacts.urls')),
    path('api/v1/communications/', include('apps.communications.urls')),
    path('api/v1/campaigns/', include('apps.campaigns.urls')),
    path('api/v1/pipelines/', include('apps.pipelines.urls')),
    path('api/v1/automations/', include('apps.automations.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Add debug toolbar URLs
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Admin site customization
admin.site.site_header = 'Communication Platform Admin'
admin.site.site_title = 'Communication Platform'
admin.site.index_title = 'Platform Administration'
