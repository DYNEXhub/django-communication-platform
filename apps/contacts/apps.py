"""
Contacts app configuration.
"""
from django.apps import AppConfig


class ContactsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contacts'
    label = 'contacts'
    verbose_name = 'Contacts'

    def ready(self):
        """Import signals when app is ready."""
        try:
            import apps.contacts.signals  # noqa F401
        except ImportError:
            pass
