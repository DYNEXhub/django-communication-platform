"""
Accounts app configuration.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    label = 'accounts'
    verbose_name = 'Accounts'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.accounts.signals  # noqa F401
        except ImportError:
            pass
