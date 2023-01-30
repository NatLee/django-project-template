from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django.conf import settings

class CacheDeco:
    def __init__(self):
        pass
    def __call__(self, func):
        if settings.CACHE_PAGE:
            @method_decorator(cache_page(settings.CACHE_TTL))
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
        else:
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
        return wrapper


