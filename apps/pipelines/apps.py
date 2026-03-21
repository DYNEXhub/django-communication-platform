"""
Pipelines app configuration.
"""
from django.apps import AppConfig


class PipelinesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pipelines'
    label = 'pipelines'
    verbose_name = 'Pipelines'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.pipelines.signals  # noqa F401
        except ImportError:
            pass
