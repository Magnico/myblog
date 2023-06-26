from myblog.settings import *

# Override or add specific Docker-related settings here

# Set DEBUG to False in Docker production environment
DEBUG = False

STATIC_ROOT = '/app/static'

# Database settings for Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myblogdb',
        'USER': 'bloguser',
        'PASSWORD': 'bloguserpassword',
        'HOST': 'db',  
        'PORT': 5432, 
    }
}

# Redis settings for Docker
REDIS_HOST = 'redis'  
REDIS_PORT = 6379  

