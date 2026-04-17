import logging
from django.core.cache import cache
from django.views.generic import ListView

logger = logging.getLogger(__name__)

class CacheListMixin:
    """
    Mixin for ListViews to automatically retrieve the entire queryset 
    from Redis cache, or query DB and cache the evaluated list.
    """
    cache_key_func = None
    cache_timeout = 300  # Default 5 min

    def get_cache_key(self):
        if self.cache_key_func:
            return self.cache_key_func()
        return None

    def get_queryset(self):
        key = self.get_cache_key()
        if not key:
            # Fallback if no key is defined
            return super().get_queryset()

        cached_qs = cache.get(key)
        if cached_qs is not None:
            logger.debug(f"{self.__class__.__name__}: cache HIT for {key}")
            return cached_qs

        logger.debug(f"{self.__class__.__name__}: cache MISS for {key} — querying database")
        
        # Evaluate QuerySet so it can be pickled
        qs_list = list(super().get_queryset())
        
        cache.set(key, qs_list, timeout=self.cache_timeout)
        return qs_list


class CacheDetailMixin:
    """
    Mixin for DetailViews to retrieve an object from cache by slug.
    We assume the object has a 'slug' field used for lookup.
    """
    cache_key_func = None
    cache_timeout = 600  # Default 10 min

    def get_cache_key(self, slug):
        if self.cache_key_func:
            return self.cache_key_func(slug)
        return None

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        if not slug:
            return super().get_object(queryset)

        key = self.get_cache_key(slug)
        if not key:
            return super().get_object(queryset)

        obj = cache.get(key)
        if obj is not None:
            logger.debug(f"{self.__class__.__name__}: cache HIT for {key}")
            return obj

        logger.debug(f"{self.__class__.__name__}: cache MISS for {key}")
        obj = super().get_object(queryset)
        cache.set(key, obj, timeout=self.cache_timeout)
        return obj


class CacheTemplateMixin:
    """
    Mixin for TemplateViews to cache the context data fully.
    """
    cache_key_func = None
    cache_timeout = 600  # Default 10 min

    def get_cache_key(self):
        if self.cache_key_func:
            return self.cache_key_func()
        return None

    def get_context_data(self, **kwargs):
        key = self.get_cache_key()
        if not key:
            return super().get_context_data(**kwargs)

        cached_context = cache.get(key)
        if cached_context is not None:
            logger.debug(f"{self.__class__.__name__}: cache HIT for {key}")
            return cached_context

        logger.debug(f"{self.__class__.__name__}: cache MISS for {key}")
        context = self.build_context_data(**kwargs)
        cache.set(key, context, timeout=self.cache_timeout)
        return context

    def build_context_data(self, **kwargs):
        """Override this method to return the full dictionary to be cached."""
        return super().get_context_data(**kwargs)
