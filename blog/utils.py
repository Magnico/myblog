from django.conf import settings
import redis

redis_conection = None

def set_redis_connection(redis_connection):
    global redis_conection
    redis_conection = redis_connection

def get_redis_connection():
    global redis_conection
    return redis_conection