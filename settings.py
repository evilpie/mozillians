# -*- coding: utf-8 -*-
# Django settings for the mozillians project.
import ldap
import logging
import os
import socket

from django.utils.functional import lazy

from django_auth_ldap.config import _LDAPConfig, LDAPSearch

# Make file paths relative to settings.
ROOT = os.path.dirname(os.path.abspath(__file__))
path = lambda *a: os.path.join(ROOT, *a)

ROOT_PACKAGE = os.path.basename(ROOT)


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {}  # See settings_local.

## Log settings
LOG_LEVEL = logging.DEBUG
HAS_SYSLOG = True
SYSLOG_TAG = "http_app_reporter"
LOGGING_CONFIG = None
LOGGING = {
    'loggers': {
        'i.landing': {'level': logging.INFO},
        'i.phonebook': {'level': logging.INFO},
    },
}


# Site ID is used by Django's Sites framework.
SITE_ID = 1


## Internationalization.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True
LOCALE_PATHS = [path('locale')]
# Gettext text domain
TEXT_DOMAIN = 'messages'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-US'

# Accepted locales
KNOWN_LANGUAGES = ('en-US', 'de', 'fr')

# List of RTL locales known to this project. Subset of LANGUAGES.
RTL_LANGUAGES = ()  # ('ar', 'fa', 'fa-IR', 'he')

LANGUAGE_URL_MAP = dict([(i.lower(), i) for i in KNOWN_LANGUAGES])


# Override Django's built-in with our native names
class LazyLangs(dict):
    def __new__(self):
        from product_details import product_details
        return dict([(lang.lower(), product_details.languages[lang]['native'])
                     for lang in KNOWN_LANGUAGES])

# Where to store product details etc.
PROD_DETAILS_DIR = path('lib/product_details_json')

LANGUAGES = lazy(LazyLangs, dict)()

# Paths that don't require a locale code in the URL.
SUPPORTED_NONLOCALES = []

# For absoluate urls
DOMAIN = socket.gethostname()
PROTOCOL = "https://"
PORT = 443

## Media and templates.

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = path('media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1iz#v0m55@h26^m6hxk3a7at*h$qj_2a$juu1#nv50548j(x1v'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'jingo.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',

    'commons.context_processors.i18n',
    #'jingo_minify.helpers.build_ids',
)

TEMPLATE_DIRS = (
    path('templates'),
)


def JINJA_CONFIG():
    import jinja2
    config = {'extensions': ['tower.template.i18n', 'jinja2.ext.do',
                             'jinja2.ext.with_', 'jinja2.ext.loopcontrols'],
              'finalize': lambda x: x if x is not None else ''}
    return config

# Bundles is a dictionary of two dictionaries, css and js, which list css files
# and js files that can be bundled together by the minify app.
MINIFY_BUNDLES = {
    'css': {
        'common': (
            'css/mozilla-base.css',
            'css/main.css',
        ),
    },
    'js': {
        'common': (
            'js/libs/jquery-1.4.4.min.js',
            'js/main.js',
        ),
    }
}


## Middlewares, apps, URL configs.

MIDDLEWARE_CLASSES = (
    'commons.middleware.LocaleURLMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'larper.middleware.LarperMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'commonware.middleware.FrameOptionsHeader',
)

# OpenLDAP
LDAP_USERS_GROUP = 'ou=people,dc=mozillians,dc=org'

# django-auth-ldap
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
)

AUTH_LDAP_USER_SEARCH = LDAPSearch(LDAP_USERS_GROUP, ldap.SCOPE_SUBTREE,
                                   "(uid=%(user)s)")
AUTH_LDAP_USER_ATTR_MAP = {"first_name": "cn", "last_name": "sn",
                           "email": "mail"}
AUTH_LDAP_PROFILE_ATTR_MAP = {"home_directory": "homeDirectory",
                              "unique_id": "uniqueIdentifier",
                              "phone": "telephoneNumber:",
                              "voucher": "mozilliansVouchedBy"}
AUTH_LDAP_ALWAYS_UPDATE_USER = False


ROOT_URLCONF = '%s.urls' % ROOT_PACKAGE

INSTALLED_APPS = (
    'landing',
    'phonebook',
    'users',
    'larper',

    # Local apps
    'commons',  # Content common to most playdoh-based apps.
    'jingo_minify',
    'tower',  # for ./manage.py extract (L10n)

    # We need this so the jsi18n view will pick up our locale directory.
    ROOT_PACKAGE,

    # Third-party apps
    'commonware.response.cookies',
    'djcelery',
    'django_nose',

    # Django contrib apps
    'django.contrib.auth',
    'django_sha2',  # Load after auth to monkey-patch it. TODO - not needed?

    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    # 'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.auth',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',

    # L10n
    'product_details',
)

# Tells the extract script what files to look for L10n in and what function
# handles the extraction. The Tower library expects this.
DOMAIN_METHODS = {
    'messages': [
        ('apps/**.py',
            'tower.management.commands.extract.extract_tower_python'),
        ('apps/**/templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
        ('templates/**.html',
            'tower.management.commands.extract.extract_tower_template'),
    ],

    ## Use this if you have localizable HTML files:
    #'lhtml': [
    #    ('**/templates/**.lhtml',
    #        'tower.management.commands.extract.extract_tower_template'),
    #],

    ## Use this if you have localizable JS files:
    #'javascript': [
        # Make sure that this won't pull in strings from external libraries you
        # may use.
    #    ('media/js/**.js', 'javascript'),
    #],
}

# Path to Java. Used for compress_assets.
JAVA_BIN = '/usr/bin/java'

## Auth
PWD_ALGORITHM = 'bcrypt'
HMAC_KEYS = {
    '2011-01-01': 'cheesecake',
}

## Tests
TEST_RUNNER = 'test_utils.runner.RadicalTestSuiteRunner'

## Celery
BROKER_HOST = 'localhost'
BROKER_PORT = 5672
BROKER_USER = 'playdoh'
BROKER_PASSWORD = 'playdoh'
BROKER_VHOST = 'playdoh'
BROKER_CONNECTION_TIMEOUT = 0.1
CELERY_RESULT_BACKEND = 'amqp'
CELERY_IGNORE_RESULT = True

SESSION_COOKIE_HTTPONLY = True
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Auth
LOGIN_URL = '/login'
