from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings modulunu təyin et
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bolbol.settings')

app = Celery('bolbol')

# Celery işlərini göndərmək üçün django settings istifadə et
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django-nun bütün asinxron tasklarını qeyd et
app.autodiscover_tasks()