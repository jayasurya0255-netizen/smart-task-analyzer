import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "replace-this-with-your-secret-key"

DEBUG = True

ALLOWED_HOSTS = []


# -----------------------------
# INSTALLED APPS
# -----------------------------
INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'backend.tasks',
]


# -----------------------------
# MIDDLEWARE (IMPORTANT ORDER)
# -----------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',   # REQUIRED
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # REQUIRED
    'django.contrib.messages.middleware.MessageMiddleware',     # REQUIRED
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# -----------------------------
# URLS
# -----------------------------
ROOT_URLCONF = "backend.task_analyzer.urls"



# -----------------------------
# TEMPLATES (REQUIRED FOR ADMIN)
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],         # keep empty unless you add templates folder
        'APP_DIRS': True,   # IMPORTANT
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


# -----------------------------
# WSGI
# -----------------------------
WSGI_APPLICATION = 'task_analyzer.wsgi.application'

CORS_ALLOW_ALL_ORIGINS = True


# -----------------------------
# DATABASE
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# -----------------------------
# PASSWORD VALIDATION
# -----------------------------
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


# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# -----------------------------
# REST FRAMEWORK CONFIG
# -----------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
}


# -----------------------------
# DEFAULT PRIMARY KEY FIELD TYPE
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
