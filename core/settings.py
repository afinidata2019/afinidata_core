"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't8qjq$d5v-pcehf8hsnhkg8)a#_^bryu3q+a@@f0+f#^&-^mtb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'areas.apps.AreasConfig',
    'milestones.apps.MilestonesConfig',
    'pages.apps.PagesConfig',
    'entities.apps.EntitiesConfig',
    'bots.apps.BotsConfig',
    'instances.apps.InstancesConfig',
    'chatfuel.apps.ChatfuelConfig',
    'messenger_users.apps.MessengerUsersConfig',
    'attributes.apps.AttributesConfig',
    'forms.apps.FormsConfig',
    'levels.apps.LevelsConfig',
    'sections.apps.SectionsConfig',
    'widget_tweaks',
    'posts.apps.PostsConfig',
    'utilities.apps.UtilitiesConfig',
    'groups.apps.GroupsConfig',
    'languages.apps.LanguagesConfig',
    'programs.apps.ProgramsConfig'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('CORE_DATABASE_ENGINE'),
        'NAME': os.getenv('CORE_DATABASE_NAME'),
        'USER': os.getenv('CORE_DATABASE_USER'),
        'PASSWORD': os.getenv('CORE_DATABASE_PASSWORD'),
        'HOST': os.getenv('CORE_DATABASE_HOST'),
        'PORT': os.getenv('CORE_DATABASE_PORT'),
    },
    'messenger_users_db': {
        'ENGINE': os.getenv('CORE_MESSENGER_USERS_DATABASE_ENGINE'),
        'NAME': os.getenv('CORE_MESSENGER_USERS_DATABASE_NAME'),
        'USER': os.getenv('CORE_MESSENGER_USERS_DATABASE_USER'),
        'PASSWORD': os.getenv('CORE_MESSENGER_USERS_DATABASE_PASSWORD'),
        'HOST': os.getenv('CORE_MESSENGER_USERS_DATABASE_HOST'),
        'PORT': os.getenv('CORE_MESSENGER_USERS_DATABASE_PORT'),
    },
    'posts_db': {
        'ENGINE': os.getenv('CORE_POSTS_DATABASE_ENGINE'),
        'NAME': os.getenv('CORE_POSTS_DATABASE_NAME'),
        'USER': os.getenv('CORE_POSTS_DATABASE_USER'),
        'PASSWORD': os.getenv('CORE_POSTS_DATABASE_PASSWORD'),
        'HOST': os.getenv('CORE_POSTS_DATABASE_HOST'),
        'PORT': os.getenv('CORE_POSTS_DATABASE_PORT'),
    }
}

DATABASE_ROUTERS = ['messenger_users.routers.MessengerUsersRouter', 'posts.routers.PostsRouter']

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Guatemala'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
DOMAIN_URL = os.getenv('CORE_DOMAIN_URL')
CONTENT_MANAGER_URL = os.getenv('CONTENT_MANAGER_URL')
CORE_ADMIN_ADMIN = os.getenv('CORE_ADMIN_ADMIN')
CORE_ADMIN_PASSWORD = os.getenv('CORE_ADMIN_PASSWORD')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'
    ]
}

LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets")
]

MESSAGE_TAGS = {
    10: 'alert-info',
    20: 'alert-info',
    25: 'alert-success',
    30: 'alert-warning',
    40: 'alert-danger'
}
