import os, sys, site

# paths we might need to pick up the project's settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'mediathread.settings_digitalocean'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
