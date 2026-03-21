"""
Configuration package for Django Communication Platform.
Imports Celery app for task queue management.
"""
from .celery import app as celery_app

__all__ = ('celery_app',)
