"""
Context processor that injects the Tianditu API key into all templates.
Keeps the key out of HTML source — only exposed server-side via template context.
The key is loaded from the TDT_KEY setting (which itself reads from environment
variable TDT_KEY, with 'YOUR_TIANDITU_API_KEY' as the placeholder fallback).
"""
import os
from django.conf import settings


def tianditu_key(request):
    # Match settings.py fallback: if env var is not set, expose the placeholder
    # so the map still renders (tiles will show a watermark until a real key is set).
    key = getattr(settings, 'TDT_KEY', 'YOUR_TIANDITU_API_KEY')
    return {'TDT_KEY': key}
