"""
Django settings for mailProject project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&znmc+x(z-&(v)2x-o!5rebsgtax#91%6c*0$!zs(#qimtxfpi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS = [
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_FROM_EMAIL = "sender@example.com"

DEFAULT_EMAIL_CONFIG = {
    'provider': "AWS",
    'username': 'user',
    'password': 'password',
    'host': 'localhost',
    'port': 3025,
    'tls': False,
    'max_retry': 2,
}

SES_CONFIGURATION_SET = "example_config_name"
