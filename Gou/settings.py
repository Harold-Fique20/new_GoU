from pathlib import Path
import os
import pyrebase
import firebase_admin
from firebase_admin import credentials, db
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5q9@&9d@m&$huwgtoe3g*a%m-c&#+du)u=f&+1^vtq0p&s(5z('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
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

ROOT_URLCONF = 'Gou.urls'

# FIREBASE
config = {
    'apiKey': 'AIzaSyDwsH9n4F80ubgz4VVxLAmZw2aeF640IfI',
    'authDomain': 'gou-v-2.firebaseapp.com',
    "databaseURL": 'firebase-adminsdk-8b7uu@gou-v-2.iam.gserviceaccount.com',
    'projectId': 'gou-v-2',
    'storageBucket': 'gou-v-2.appspot.com',
    'messagingSenderId': '1072778966687',
    'appId': '1:1072778966687:web:8581d8dc4b5733329c14aa',
    'measurementId': 'G-L4X0HBZ3GS',
}

firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()
 

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'Gou.wsgi.application'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com' # por ejemplo: 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gou2udec@gmail.com' 
EMAIL_HOST_PASSWORD = 'gou22024' 



# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

'''DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': '<Gou>',
        'HOST': 'mongodb+srv://GoU:<gou22024>@clustergou.0rlnvqb.mongodb.net/?retryWrites=true&w=majority&appName=ClusterGoU',
    }
}'''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}




LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'accounts/static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

