import os
from os.path import join, abspath, dirname
from django.contrib.messages import constants as message_constants
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

# utility functions for handling paths inside the project
here = lambda *x: join(abspath(dirname(__file__)), *x)
PROJECT_ROOT = here("..", "..")
root = lambda *x: join(abspath(PROJECT_ROOT), *x)


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Nate Aune', 'nate@appsembler.com'),
    ('Filip Jukic', 'filip@appsembler.com'),
)

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = 'support@appsembler.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': root('launcher.db'),  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    '.appsembler.com',
    '.dev',
    '.jukic.me',
    '127.0.0.1',
    '192.168.33.10',
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = root('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = root('collected_static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    root('static'),
    root('components/bower_components'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'pipeline.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
    #'pipeline.finders.CachedFileFinder',

)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = get_env_variable('SECRET_KEY')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",

    # allauth specific context processors
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'launcher.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'launcher.wsgi.application'

TEMPLATE_DIRS = (
    root('templates'),
)

INSTALLED_APPS = (
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Third-party apps
    'allauth',
    'allauth.account',
    'djangobower',
    'django_extensions',
    'kombu.transport.django',
    'pipeline',
    'tastypie',

    # Project apps
    'deployment',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
        'celery': {
            'level': 'WARNING',
            'handlers': ['sentry'],
            'propagate': False,
        },
        'deployment.tasks': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

MESSAGE_LEVEL = message_constants.SUCCESS

# Bower config
BOWER_COMPONENTS_ROOT = root('components')

BOWER_INSTALLED_APPS = (
    'jquery#1.9.1',
    'underscore#1.6.0',
    'backbone#1.1.2',
    'json2',
    'kbwood_countdown#1.6.2',
    'bootstrap#3.1.1',
)

# Django Pipeline config

PIPELINE_CSS = {
    'launcher_main': {
        'source_filenames': (
            'bootstrap/dist/css/bootstrap.css',
            'bootstrap/dist/css/bootstrap-theme.css',
            'css/app.css'
        ),
        'output_filename': 'css/launcher_main.css',
        'extra_context': {
            'media': 'screen',
        },
    },
}

PIPELINE_JS = {
    'launcher_main': {
        'source_filenames': (
            'jquery/jquery.js',
            'json2/json2.js',
            'underscore/underscore.js',
            'backbone/backbone.js',
            'bootstrap/dist/js/bootstrap.js',
        ),
        'output_filename': 'js/launcher_main.min.js',
    },
    'app': {
        'source_filenames': (
            'js/app.js',
        ),
        'output_filename': 'js/app.min.js'

    },
    'countdown': {
        'source_filenames': (
            'kbwood_countdown/jquery.countdown.js',
        ),
        'output_filename': 'js/countdown.min.js'

    },
}

PIPELINE_COMPILERS = (
    'pipeline.compilers.less.LessCompiler',
)

# npm install -g uglify-js
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.uglifyjs.UglifyJSCompressor'
PIPELINE_UGLIFYJS_BINARY = '/usr/bin/env uglifyjs'

# Allauth config
AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Launcher] "
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/'
EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_ON_EMAIL_CONFIRMATION = False
SIGNUP_PASSWORD_VERIFICATION = False

# Trial settings
DEFAULT_UNCONFIRMED_TRIAL_DURATION = 30
DEFAULT_TRIAL_DURATION = 120

# Celery config
BROKER_URL = 'django://'
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_RESULT_BACKEND = None
CELERY_IGNORE_RESULT = True
CELERY_DEFAULT_QUEUE = 'celery'
CELERY_CREATE_MISSING_QUEUES = True

# Pusher settings
PUSHER_APP_ID = get_env_variable('PUSHER_APP_ID')
PUSHER_APP_KEY = get_env_variable('PUSHER_APP_KEY')
PUSHER_APP_SECRET = get_env_variable('PUSHER_APP_SECRET')

# Customer.io settings
CUSTOMERIO_SITE_ID = get_env_variable('CUSTOMERIO_SITE_ID')
CUSTOMERIO_API_KEY = get_env_variable('CUSTOMERIO_API_KEY')

# Intercom.io settings
INTERCOM_APP_ID = get_env_variable('INTERCOM_APP_ID')
INTERCOM_API_KEY = get_env_variable('INTERCOM_API_KEY')
INTERCOM_EDX_APP_ID = get_env_variable('INTERCOM_EDX_APP_ID')
INTERCOM_EDX_APP_SECRET = get_env_variable('INTERCOM_EDX_APP_SECRET')

# Docker settings
SHIPYARD_HOST = get_env_variable('SHIPYARD_HOST')
SHIPYARD_KEY = get_env_variable('SHIPYARD_KEY')
HIPACHE_REDIS_IP = get_env_variable('HIPACHE_REDIS_IP')
HIPACHE_REDIS_PORT = get_env_variable('HIPACHE_REDIS_PORT')

# Domain from where demo apps are served, example: demo.appsembler.com
DEMO_APPS_CUSTOM_DOMAIN = get_env_variable('DEMO_APPS_CUSTOM_DOMAIN')

# Default settings for app containers
DEFAULT_NUMBER_OF_CPUS = 0.1
DEFAULT_AMOUNT_OF_RAM = 128

