"""
Automations app configuration.
"""
from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.automations'
    label = 'automations'
    verbose_name = 'Automations'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.automations.signals  # noqa F401
        except ImportError:
            pass
