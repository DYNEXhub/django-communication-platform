"""
Communications app configuration.
"""
from django.apps import AppConfig


class CommunicationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.communications'
    label = 'communications'
    verbose_name = 'Communications'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.communications.signals  # noqa F401
        except ImportError:
            pass
