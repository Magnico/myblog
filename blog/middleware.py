from django.conf import settings
from django.urls import resolve
import redis

class RedisVisitMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

    def __call__(self, request):
        response = self.get_response(request)
        name = resolve(request.path_info).url_name
        if request.method == 'GET' and name == 'post_detail':
            post_pk = resolve(request.path_info).kwargs.get('pk')
            if post_pk:
                key = f'post:{post_pk}:visits'
                self.redis.incr(key)
        return response