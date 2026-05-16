import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

def _env_bool(name, default='False'):
    return os.getenv(name, default).strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name, default=''):
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(',') if item.strip()]


DEBUG = _env_bool('DEBUG', 'True')

if DEBUG:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
else:
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('SECRET_KEY must be set when DEBUG is False')

allowed_hosts_str = os.getenv('ALLOWED_HOSTS')
if allowed_hosts_str:
    if allowed_hosts_str.strip() == '*':
        ALLOWED_HOSTS = ['*']
    else:
        ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]
elif DEBUG:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    raise RuntimeError('ALLOWED_HOSTS must be set when DEBUG is False')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'monitor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fermentiq_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'fermentiq_backend.wsgi.application'

DATABASES = {
    # Default: use SQLite for local development
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If a DATABASE_URL environment variable is provided, use it.
# Requires dj-database-url in requirements.
if os.getenv('DATABASE_URL'):
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(
            os.environ['DATABASE_URL'],
            conn_max_age=int(os.getenv('DATABASE_CONN_MAX_AGE', '600')),
        )
    except Exception:
        # Fall back to the default SQLite DB if parsing fails
        pass

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = _env_bool('CORS_ALLOW_ALL_ORIGINS', 'True' if DEBUG else 'False')
CORS_ALLOWED_ORIGINS = _env_list('CORS_ALLOWED_ORIGINS')
CSRF_TRUSTED_ORIGINS = _env_list('CSRF_TRUSTED_ORIGINS')
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = _env_bool('USE_X_FORWARDED_HOST', 'True')
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000' if not DEBUG else '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True' if not DEBUG else 'False')
SECURE_HSTS_PRELOAD = _env_bool('SECURE_HSTS_PRELOAD', 'False')
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'same-origin')
X_FRAME_OPTIONS = 'DENY'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
