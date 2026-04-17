"""
cache_utils.py
--------------
Centralised Redis cache key definitions, TTL constants, and invalidation helpers.

This module is the single source of truth for all cache keys in the project.
Both views.py (reads/writes) and signals.py (busts) import from here to
guarantee consistency — changing a key name here automatically fixes both.

Cache Flow
----------

  HTTP Request
       │
       ▼
   views.py ──► cache.get(key)
                    │
           ┌────────┴────────┐
           │ HIT             │ MISS
           ▼                 ▼
      Return cached    Query RDS/SQLite
      data (Redis)     │
      (0 DB queries)   ▼
                   cache.set(key, data, ttl)
                       │
                       ▼
                  Return fresh data

  Admin saves model
       │
       ▼
  post_save signal ──► bust_*(slug) ──► cache.delete(key)
                                           │
                                           ▼
                              Next request rebuilds from DB

TTL Guidelines
--------------
  HOME          5 min  — composite of many models, busted by many signals
  DETAIL        10 min — slug-based pages, busted per slug on save
  LIST          5 min  — paginated collections, busted on any item save
  CATEGORIES    30 min — rarely changes, busted on any blogpost save
  STATIC PAGES  1 hour — policy pages, busted when admin edits them
  ABOUT/CONTACT 10 min — company info, busted on save
"""

import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TTL constants (seconds)
# ---------------------------------------------------------------------------
TTL_HOME = 300          # 5 minutes  — home page (many queries)
TTL_DETAIL = 600        # 10 minutes — service / subject / blog detail
TTL_LIST = 300          # 5 minutes  — paginated list views
TTL_CATEGORIES = 1800   # 30 minutes — blog/work categories (low churn)
TTL_STATIC = 3600       # 60 minutes — privacy / terms / refund policy
TTL_ABOUT = 600         # 10 minutes — about + contact pages


# ---------------------------------------------------------------------------
# Cache key builders
# All keys are strings; django-redis's KEY_PREFIX ("oah:") is prepended
# automatically by the cache backend.
# ---------------------------------------------------------------------------

def key_home():
    """Home page composite data (hero, services, subjects, FAQs, …)."""
    return "home_page"


def key_service_list():
    """Full active service list (evaluated, stored as Python list)."""
    return "service_list:all"


def key_service_detail(slug: str):
    """Individual service by slug."""
    return f"service:{slug}"


def key_subject_list():
    """Full active subject list (evaluated, stored as Python list)."""
    return "subject_list:all"


def key_subject_detail(slug: str):
    """Individual subject by slug."""
    return f"subject:{slug}"


def key_blog_categories():
    """Distinct list of blog post categories."""
    return "blog_categories"


def key_blog_detail(slug: str):
    """Individual published blog post by slug."""
    return f"blog:{slug}"


def key_about():
    """About page composite (about_page, core_values, milestones)."""
    return "about_page"


def key_contact():
    """Contact page settings."""
    return "contact_page"


def key_privacy():
    """Privacy Policy content object."""
    return "privacy_policy"


def key_terms():
    """Terms & Conditions content object."""
    return "terms_conditions"


def key_refund():
    """Refund Policy content object."""
    return "refund_policy"


# ---------------------------------------------------------------------------
# Invalidation helpers
# Each function deletes the exact set of cache keys that could be stale
# after a specific model is saved / deleted in the admin.
# ---------------------------------------------------------------------------

def _delete(*keys):
    """
    Delete one or more cache keys and log the operation.
    Safe to call even when cache backend is unavailable
    (IGNORE_EXCEPTIONS=True in settings ensures no exception is raised).
    """
    for key in keys:
        result = cache.delete(key)
        logger.info("Cache busted: key=%s deleted=%s", key, result)


def bust_home():
    """
    Called when any model that contributes data to the home page changes:
    HeroSection, CTABanner, FAQ, Testimonial, Guide, Tool, SampleWork.
    """
    _delete(key_home())


def bust_service(slug: str = None):
    """
    Called when a Service is saved or deleted.

    Busts:
      - The detail page for that specific service (if slug provided).
      - The full service list (used by service_list view + home page).
      - The home page (services appear in the homepage section).
    """
    keys = [key_service_list(), key_home()]
    if slug:
        keys.append(key_service_detail(slug))
    _delete(*keys)


def bust_subject(slug: str = None):
    """
    Called when a Subject is saved or deleted.

    Busts:
      - The detail page for that specific subject (if slug provided).
      - The full subject list (used by subject_list view + home page).
      - The home page (subjects appear in the homepage section).
    """
    keys = [key_subject_list(), key_home()]
    if slug:
        keys.append(key_subject_detail(slug))
    _delete(*keys)


def bust_blog(slug: str = None):
    """
    Called when a BlogPost is saved or deleted.

    Busts:
      - The detail page for that post (if slug provided).
      - The categories list (a new post may introduce a new category).
    Note: blog_list itself is NOT cached (search/filters make it dynamic).
    """
    keys = [key_blog_categories()]
    if slug:
        keys.append(key_blog_detail(slug))
    _delete(*keys)


def bust_about():
    """Called when AboutPage, CoreValue, or Milestone changes."""
    _delete(key_about())


def bust_contact():
    """Called when ContactPage changes."""
    _delete(key_contact())


def bust_static_pages():
    """Called when PrivacyPolicy, TermsCondition, or RefundPolicy changes."""
    _delete(key_privacy(), key_terms(), key_refund())
