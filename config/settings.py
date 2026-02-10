"""
Django settings for config project.
Configuration DEV stable ESFE
"""

from pathlib import Path

# ==================================================
# BASE
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ==================================================
# SECURITY
# ==================================================
SECRET_KEY = "django-insecure-change-this-key-later"

DEBUG = True

ALLOWED_HOSTS = []


# ==================================================
# APPLICATIONS
# ==================================================
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # ⚠️ OBLIGATOIRE AVANT TOUT COMPONENT
    "django_components",

    # Dev tools
    "django_browser_reload",

    # UI / Core
    "ui.apps.UiConfig",
    "core",

    # Métier
    "admissions.apps.AdmissionsConfig",
    "inscriptions.apps.InscriptionsConfig",
    "payments.apps.PaymentsConfig",
    "students",
    "formations",

    # Contenu
    "blog",
    "news",
]

# ==================================================
# DJANGO-COMPONENTS CONFIG
# ==================================================
COMPONENTS = {
    "template_cache_size": 128,
}


# ==================================================
# MIDDLEWARE
# ==================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # Live reload
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]


# ==================================================
# URLS / WSGI
# ==================================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# ==================================================
# TEMPLATES (⚠️ PARTIE LA PLUS IMPORTANTE)
# ==================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # Templates globaux
        "DIRS": [BASE_DIR / "templates"],

        # ⚠️ OBLIGATOIRE POUR django-components
        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],

            # ⚠️ IMPORTANT : builtin components
            "builtins": [
                "django_components.templatetags.component_tags",
            ],
        },
    },
]


# ==================================================
# DATABASE
# ==================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==================================================
# PASSWORD VALIDATION
# ==================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ==================================================
# INTERNATIONALIZATION
# ==================================================
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ==================================================
# STATIC FILES
# ==================================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# PROD plus tard
# STATIC_ROOT = BASE_DIR / "staticfiles"


# ==================================================
# MEDIA FILES
# ==================================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==================================================
# DEFAULT PK
# ==================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==================================================
# EMAIL (DEV)
# ==================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "ESFE <no-reply@esfe-mali.org>"
STUDENT_LOGIN_URL = "http://127.0.0.1:8000/student/login/"
