"""
Django settings for simple_mud project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys
import os
import datetime
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'k!hs*9mg-(de6k3jku)h5l(-2z6214$h#3akiw^ujglyj3(7_a'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mud'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'simple_mud.urls'

WSGI_APPLICATION = 'simple_mud.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            "timeout": 20
        }
    }
}

POSTGRES_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'simplemud',
        'USER': 'simplemud',
        'PASSWORD': 'qwerty876543dfgVBGT^',
        'HOST': 'localhost',
        'PORT': '',
        }
}

DATABASES = POSTGRES_DATABASES

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
# BROKER_URL = "amqp://guest@toby-desktop//"
# CELERY_RESULT_BACKEND = "amqp://guest@toby-desktop//"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

ROUND_TIME = 1
REGEN_TIME = 2 * 60
HEAL_TIME = 1 * 60

CELERYBEAT_SCHEDULE = {
    'round-time': {
        'task': 'mud.tasks.perform_round_task',
        'schedule': datetime.timedelta(seconds=ROUND_TIME)
    },
    'regen-time': {
        'task': 'mud.tasks.perform_regen_task',
        'schedule': datetime.timedelta(seconds=REGEN_TIME)
    },
    'heal-time': {
        'task': 'mud.tasks.perform_heal_task',
        'schedule': datetime.timedelta(seconds=HEAL_TIME)
    },
}

BASE_LOG_FOLDER = '/home/tnance/logs'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
         }
     },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'simplemud_logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(BASE_LOG_FOLDER, "simplemud.log"),
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream':sys.stdout,
            'formatter': 'standard'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        }
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['console', 'mail_admins','simplemud_logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'simplemud_logfile'],
            'level': 'WARN',
            'propagate': False,
        },
        'nose.plugins': {
            'handlers': ['console', 'simplemud_logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        'analytical.templatetags': {
            'handlers': ['console', 'simplemud_logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        'mud': {
            'handlers': ['console', 'simplemud_logfile'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'simplemud_logfile'],
            'propagate': False,
            'level': 'WARN',
        },
    }
}
