import os
from django.core.exceptions import ImproperlyConfigured
from settings_shared import *


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

DEBUG = False
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
    },
    'johnny': dict(
        BACKEND='johnny.backends.memcached.PyLibMCCache',
        LOCATION=['127.0.0.1:11211'],
        JOHNNY_CACHE=True,
    )
}

MIDDLEWARE_CLASSES = ('django.middleware.cache.UpdateCacheMiddleware',) + \
                    MIDDLEWARE_CLASSES + \
                    ('django.middleware.cache.FetchFromCacheMiddleware',)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{app_name}}',
        'HOST': 'localhost',
        'USER': '{{app_name}}',
        'PASSWORD': '{{postgres_password}}',
    }
}

SECRET_KEY = '{{secret_key}}'

ALLOWED_HOSTS = [
    'mediathread.appsembler.com',
    '.mediathread.appsembler.com',
    '107.170.23.107'
]

MEDIA_ROOT = '{{django_media_dir}}'
MEDIA_URL = '/media/'
STATIC_ROOT = '{{django_static_dir}}'

COMPRESS_ENABLED = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = 'https://{{cloudfront_url}}/'
COMPRESS_STORAGE = 'mediathread.s3_utils.CachedStaticRootS3BotoStorage'
STATICFILES_STORAGE = COMPRESS_STORAGE
COMPRESS_OFFLINE = True
COMPRESS_JS_FILTERS = []
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter'
]
AWS_IS_GZIPPED = True
AWS_QUERYSTRING_EXPIRE = 63115200
AWS_S3_SECURE_URLS = True
AWS_S3_CUSTOM_DOMAIN = '{{cloudfront_url}}'

STATIC_URL = COMPRESS_URL

# Customer.io keys
CUSTOMERIO_SITE_ID = '{{customerio_site_id}}'
CUSTOMERIO_API_KEY = '{{customerio_api_key}}'

# Mailchimp arguments
MAILCHIMP_API_KEY = '{{mailchimp_api_key}}'
MAILCHIMP_REGISTRATION_LIST_ID = '{{mailchimp_registration_list_id}}'

# Segment.io key
SEGMENTIO_API_KEY = '{{segmentio_api_key}}'
SEGMENTIO_JS_KEY = '{{segmentio_js_key}}'

# Amazon AWS keys for S3 storage
AWS_ACCESS_KEY_ID = '{{aws_access_key_id}}'
AWS_SECRET_ACCESS_KEY = '{{aws_secret_access_key}}'
AWS_PRELOAD_METADATA = True
AWS_STORAGE_BUCKET_NAME = 'mediathread_do'

# Flick API key for clipping photos
DJANGOSHERD_FLICKR_APIKEY = '{{djangosherd_flickr_apikey}}'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = '{{mandrill_username}}'
EMAIL_HOST_PASSWORD = '{{mandrill_api_key}}'
DEFAULT_FROM_EMAIL = "support@appsembler.com"
SERVER_EMAIL = "support@appsembler.com"
PUBLIC_CONTACT_EMAIL = "support@appsembler.com"
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Mediathread] '

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': '{{sentry_dsn}}',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    }
}