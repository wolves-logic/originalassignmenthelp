"""
processor.py
------------
Global template context processor.

Every Django template render calls this function and receives the returned
dictionary merged into the template context. Without caching this means
4 database queries on EVERY page load (including static pages, admin, etc.).

With caching (ElastiCache or LocMemCache):
  - The first request after a cache miss hits the database (4 queries).
  - All subsequent requests within the TTL window hit Redis instead — O(1).
  - Stale cache is automatically busted by post_save signals in signals.py
    whenever an admin changes OfferBanner, Service, Subject, or SiteSettings.

Cache key: ``oah:global_site_data``
TTL      : 5 minutes (300 seconds) — configurable via GLOBAL_CONTEXT_CACHE_TTL
"""

import logging

from django.core.cache import cache

from .models import OfferBanner, Service, Subject, SiteSettings

logger = logging.getLogger(__name__)

# Cache key used by both this processor and the invalidation signals
GLOBAL_CONTEXT_CACHE_KEY = "global_site_data"

# How long (in seconds) the cached data lives before being refreshed
# from the database.  5 minutes is a sensible default for a CMS site;
# lower it if offer banners need to update instantly.
GLOBAL_CONTEXT_CACHE_TTL = 300


def global_context(request):
    """
    Build (or serve from cache) the site-wide template context variables.

    Returns
    -------
    dict with keys:
        offer         : active OfferBanner instance (or None)
        menu_services : up to 5 Service instances marked show_in_menu=True
        menu_subjects : up to 5 Subject instances marked show_in_menu=True
        site_settings : SiteSettings singleton (or None)
    """
    # Try to fetch the pre-built context dict from cache.
    # With ElastiCache this is a single Redis GET — microseconds, not milliseconds.
    cached = cache.get(GLOBAL_CONTEXT_CACHE_KEY)

    if cached is not None:
        # Cache hit — return immediately without touching the database
        logger.debug("global_context: cache HIT")
        return cached

    # Cache miss — build the context by querying the database.
    logger.debug("global_context: cache MISS — querying database")

    try:
        # Query 1: active offer banner (used in the header ribbon)
        offer = OfferBanner.objects.filter(is_active=True).last()

        # Query 2: services shown in the navigation dropdown (max 5)
        menu_services = list(
            Service.objects.filter(is_active=True, show_in_menu=True)[:5]
        )

        # Query 3: subjects shown in the navigation dropdown (max 5)
        menu_subjects = list(
            Subject.objects.filter(is_active=True, show_in_menu=True)[:5]
        )

        # Query 4: singleton site-wide settings (email, phone, social links, etc.)
        site_settings = SiteSettings.objects.first()

        context = {
            "offer": offer,
            "menu_services": menu_services,
            "menu_subjects": menu_subjects,
            "site_settings": site_settings,
        }

        # Store in cache.
        cache.set(GLOBAL_CONTEXT_CACHE_KEY, context, timeout=GLOBAL_CONTEXT_CACHE_TTL)
        logger.debug(
            "global_context: cached for %s seconds", GLOBAL_CONTEXT_CACHE_TTL
        )
    except Exception as e:
        logger.exception("global_context error: fallback to empty context")
        context = {
            "offer": None,
            "menu_services": [],
            "menu_subjects": [],
            "site_settings": None,
        }

    return context
