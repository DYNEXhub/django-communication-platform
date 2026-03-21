"""
Development settings for Django Communication Platform.
Includes debug toolbar and permissive CORS.
"""
from .base import *

# Development mode
DEBUG = True

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Add debug toolbar for development
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
] + MIDDLEWARE

# Internal IPs for debug toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Debug toolbar configuration
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Allow insecure cookies in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Celery eager mode for development (run tasks synchronously)
CELERY_TASK_ALWAYS_EAGER = False  # Set to True to disable async in dev
CELERY_TASK_EAGER_PROPAGATES = True
