"""
Campaigns app configuration.
"""
from django.apps import AppConfig


class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.campaigns'
    label = 'campaigns'
    verbose_name = 'Campaigns'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.campaigns.signals  # noqa F401
        except ImportError:
            pass
