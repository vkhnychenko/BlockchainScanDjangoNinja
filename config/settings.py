import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG"))

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'wallets',
    'channels',
    'telegram_bot',
    'django_celery_beat'
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

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("POSTGRES_ENGINE"),
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 60 * 24

#Celery settings
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')


#Blockchain settings
ETH_API_URL: str = 'https://api.etherscan.io/api'
ETH_API_KEY = os.environ.get("ETH_API_KEY")

BSC_API_URL: str = 'https://api.bscscan.com/api'
BSC_API_KEY = os.environ.get("BSC_API_KEY")

POLYGON_API_URL: str = 'https://api.polygonscan.com/api'
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY")

MORALIS_BASE_URL = os.environ.get("MORALIS_BASE_URL")
MORALIS_API_KEY = os.environ.get("MORALIS_API_KEY")

ONE_INCH_BASE_URL = "https://api.1inch.exchange/v3.0"
TETHER_CONTRACT = '0xdac17f958d2ee523a2206206994597c13d831ec7'
INFURA_URL = os.environ.get("INFURA_URL")
CHAIN_DECIMALS = {'eth': 18, 'bsc': 18, 'polygon': 18}

#BOT settings
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BASE_SERVER_URL = os.environ.get("BASE_SERVER_URL")
BASE_SERVER_WS = os.environ.get("BASE_SERVER_WS")
BOT_ADMINS = os.environ.get('BOT_ADMINS').split(',')
SERVER_API_KEY = os.environ.get('SERVER_API_KEY')
DONATE_WALLET = '0xEe7cABe78FBd21BBBD7649234E0002A86Aa1fF8d'

LOCALES_DIR = BASE_DIR / 'telegram_bot/locales'
I18N_DOMAIN = 'BlockchainScanBot'

URLS_SCAN = {
    'eth': 'https://etherscan.io/',
    'bsc': 'https://bscscan.com/',
    'polygon': 'https://polygonscan.com/'
}


NATIVE_CURRENCY = {
    'eth': 'ETH',
    'bsc': 'BNB',
    'polygon': 'POLYGON'
}

