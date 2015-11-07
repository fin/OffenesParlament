from __future__ import absolute_import
import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'offenesparlament.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

from configurations import importer
importer.install()

from django.conf import settings

app = Celery('offenesparlament')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
