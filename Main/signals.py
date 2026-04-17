"""
signals.py
----------
Django signals that automatically clean up media files whenever a record
is deleted or its file fields are replaced in the Django admin.

How it works
------------
All deletions go through Django's storage API (`field.storage.delete(name)`)
instead of raw `os.remove()` calls. This makes the cleanup logic
storage-backend-agnostic:

  - Local development (USE_S3=False)  →  deletes the file from disk
  - Production      (USE_S3=True)     →  deletes the object from S3

This means no extra boto3 calls are needed here; django-storages handles
the underlying AWS API call transparently.

Signals registered
------------------
  post_delete / pre_save  →  BlogPost    (thumbnail + CKEditor content images)
  post_delete / pre_save  →  HeroSection (hero_image)
"""

import re
import logging

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import (
    BlogPost, HeroSection, OfferBanner, Service, Subject, SiteSettings,
    CTABanner, FAQ, Testimonial, Guide, Tool, SampleWork,
    AboutPage, CoreValue, Milestone, ContactPage,
    PrivacyPolicy, TermsCondition, RefundPolicy,
)

# Use Django's logger so output goes to the configured logging backend
# (file, console, Sentry, etc.) rather than bare print() calls.
logger = logging.getLogger(__name__)


# ===========================================================================
# Cache invalidation signals
# ===========================================================================
#
# Two layers of cache are busted here:
#
# 1. GLOBAL CONTEXT cache (processor.py) — the 4 queries that run on every
#    page (offer banner, menu services/subjects, site settings).
#    Key: GLOBAL_CONTEXT_CACHE_KEY
#
# 2. VIEW-LEVEL cache (views.py) — per-view query results stored by
#    cache_utils helpers (home_page, service:slug, blog_categories, …).
#
# Every post_save signal calls the appropriate bust_*() helper from
# cache_utils.py, which deletes the exact keys that are now stale.
# ===========================================================================

# Import shared keys from the two cache modules
from .processor import GLOBAL_CONTEXT_CACHE_KEY          # noqa: E402
from .cache_utils import (                                # noqa: E402
    bust_home, bust_service, bust_subject, bust_blog,
    bust_about, bust_contact, bust_static_pages,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _bust_global_context_cache():
    """
    Delete the global nav/header/footer context cache entry.
    Safe when cache backend is unavailable (IGNORE_EXCEPTIONS=True).
    """
    deleted = cache.delete(GLOBAL_CONTEXT_CACHE_KEY)
    logger.info(
        "global_context cache busted (key=%s, deleted=%s)",
        GLOBAL_CONTEXT_CACHE_KEY,
        deleted,
    )


# ---------------------------------------------------------------------------
# Global context invalidation — header/footer/nav data
# ---------------------------------------------------------------------------

@receiver(post_save, sender=OfferBanner)
def invalidate_cache_on_offer_change(sender, instance, **kwargs):
    """Offer banner in site header changed."""
    _bust_global_context_cache()


@receiver(post_save, sender=SiteSettings)
def invalidate_cache_on_sitesettings_change(sender, instance, **kwargs):
    """Site-wide settings (email, phone, social links) changed."""
    _bust_global_context_cache()


# ---------------------------------------------------------------------------
# Service invalidation — home page + list + detail + global nav
# ---------------------------------------------------------------------------

@receiver(post_save, sender=Service)
def invalidate_cache_on_service_change(sender, instance, **kwargs):
    """
    A service was saved in admin — bust:
      • service detail cache for THIS slug
      • service list cache (full collection)
      • home page cache (services section)
      • global context cache (show_in_menu services)
    """
    bust_service(slug=instance.slug)
    _bust_global_context_cache()


@receiver(post_delete, sender=Service)
def invalidate_cache_on_service_delete(sender, instance, **kwargs):
    """A service was hard-deleted — bust same keys as save."""
    bust_service(slug=instance.slug)
    _bust_global_context_cache()


# ---------------------------------------------------------------------------
# Subject invalidation — home page + list + detail + global nav
# ---------------------------------------------------------------------------

@receiver(post_save, sender=Subject)
def invalidate_cache_on_subject_change(sender, instance, **kwargs):
    """
    A subject was saved — bust:
      • subject detail cache for THIS slug
      • subject list cache
      • home page cache (subjects section)
      • global context cache (show_in_menu subjects)
    """
    bust_subject(slug=instance.slug)
    _bust_global_context_cache()


@receiver(post_delete, sender=Subject)
def invalidate_cache_on_subject_delete(sender, instance, **kwargs):
    """A subject was hard-deleted."""
    bust_subject(slug=instance.slug)
    _bust_global_context_cache()


# ---------------------------------------------------------------------------
# Blog post invalidation
# ---------------------------------------------------------------------------

@receiver(post_save, sender=BlogPost)
def invalidate_cache_on_blog_change(sender, instance, **kwargs):
    """
    A blog post was saved — bust:
      • blog detail cache for THIS slug
      • blog categories list (a new post may introduce a new category)
    Blog list is never cached (search makes it dynamic).
    """
    bust_blog(slug=instance.slug)


@receiver(post_delete, sender=BlogPost)
def invalidate_cache_on_blog_delete(sender, instance, **kwargs):
    """A blog post was hard-deleted."""
    bust_blog(slug=instance.slug)


# ---------------------------------------------------------------------------
# Home page composition — any of these models feeds into home_page cache
# ---------------------------------------------------------------------------

@receiver(post_save, sender=HeroSection)
def invalidate_cache_on_hero_change(sender, instance, **kwargs):
    """Hero banner changed — bust home page."""
    bust_home()


@receiver(post_save, sender=CTABanner)
def invalidate_cache_on_cta_change(sender, instance, **kwargs):
    """CTA banner changed — bust home page."""
    bust_home()


@receiver(post_save, sender=FAQ)
def invalidate_cache_on_faq_change(sender, instance, **kwargs):
    """FAQ list changed — bust home page."""
    bust_home()


@receiver(post_save, sender=Testimonial)
def invalidate_cache_on_testimonial_change(sender, instance, **kwargs):
    """Testimonials changed — bust home page."""
    bust_home()


@receiver(post_save, sender=Guide)
def invalidate_cache_on_guide_change(sender, instance, **kwargs):
    """Guide added/updated — bust home page (recent_guides section)."""
    bust_home()


@receiver(post_save, sender=Tool)
def invalidate_cache_on_tool_change(sender, instance, **kwargs):
    """Tool added/updated — bust home page (recent_tools section)."""
    bust_home()


@receiver(post_save, sender=SampleWork)
def invalidate_cache_on_samplework_change(sender, instance, **kwargs):
    """Sample work added/updated — bust home page (recent_samples section)."""
    bust_home()


# ---------------------------------------------------------------------------
# About page
# ---------------------------------------------------------------------------

@receiver(post_save, sender=AboutPage)
@receiver(post_save, sender=CoreValue)
@receiver(post_save, sender=Milestone)
def invalidate_cache_on_about_change(sender, instance, **kwargs):
    """Any about page component changed — bust about page cache."""
    bust_about()


# ---------------------------------------------------------------------------
# Contact page
# ---------------------------------------------------------------------------

@receiver(post_save, sender=ContactPage)
def invalidate_cache_on_contact_change(sender, instance, **kwargs):
    """Contact page settings changed."""
    bust_contact()


# ---------------------------------------------------------------------------
# Legal / policy pages
# ---------------------------------------------------------------------------

@receiver(post_save, sender=PrivacyPolicy)
@receiver(post_save, sender=TermsCondition)
@receiver(post_save, sender=RefundPolicy)
def invalidate_cache_on_policy_change(sender, instance, **kwargs):
    """Any policy page updated — bust all static page caches."""
    bust_static_pages()


# ===========================================================================
# File cleanup signals (storage-agnostic: works with local disk and S3)
# ===========================================================================

def _delete_file(file_field):
    """
    Delete the file referenced by a FileField / ImageField using whatever
    storage backend is currently configured (local filesystem or S3).

    Parameters
    ----------
    file_field : FieldFile
        An ImageField or FileField descriptor attached to a model instance,
        e.g. ``instance.thumbnail_image``.

    Notes
    -----
    We call ``file_field.storage.delete(file_field.name)`` rather than
    ``default_storage.delete(...)`` to guarantee we use exactly the same
    storage backend that the field itself is bound to. This prevents
    accidental cross-backend deletions if multiple backends are configured.
    """
    if not file_field or not file_field.name:
        return  # Nothing to do

    try:
        storage = file_field.storage
        if storage.exists(file_field.name):
            storage.delete(file_field.name)
            logger.info("Deleted file from storage: %s", file_field.name)
        else:
            logger.warning(
                "File not found in storage (already deleted?): %s",
                file_field.name,
            )
    except Exception:
        logger.exception("Error deleting file from storage: %s", file_field.name)


# ---------------------------------------------------------------------------
# Helper: extract storage-relative names from CKEditor HTML content
# ---------------------------------------------------------------------------

def _extract_storage_names_from_html(html_content):
    """
    Parse CKEditor-generated HTML and return a list of storage-relative
    file names for every inline image that belongs to our media storage.

    How the URL → storage name conversion works
    -------------------------------------------
    Django's FileField stores the *relative* name (the S3 key suffix, or the
    path relative to MEDIA_ROOT) inside the database.  The full public URL is
    ``MEDIA_URL + name``.

    Example (S3):
        MEDIA_URL = "https://mybucket.s3.amazonaws.com/media/"
        src URL   = "https://mybucket.s3.amazonaws.com/media/uploads/img.png"
        name      = "uploads/img.png"

    Example (local):
        MEDIA_URL = "/media/"
        src URL   = "/media/uploads/img.png"
        name      = "uploads/img.png"

    Parameters
    ----------
    html_content : str
        Raw HTML string from a CKEditor5Field.

    Returns
    -------
    list[str]
        Storage-relative names ready to pass to ``storage.delete(name)``.
    """
    if not html_content:
        return []

    media_url = settings.MEDIA_URL  # e.g. "/media/" or "https://..."

    # Match src="<media_url><anything>" — handles both relative and absolute URLs
    pattern = r'src=["\'](' + re.escape(media_url) + r'[^"\']+)["\']'
    matches = re.findall(pattern, html_content)

    names = []
    for full_url in matches:
        # Strip the MEDIA_URL prefix to get the storage-relative name
        relative_name = full_url[len(media_url):]
        if relative_name:
            names.append(relative_name)

    return names


def _delete_content_images(html_content):
    """
    Delete every inline image embedded in CKEditor HTML content from storage.

    Parameters
    ----------
    html_content : str
        Raw HTML from a CKEditor5Field.
    """
    from django.core.files.storage import default_storage  # lazy import

    names = _extract_storage_names_from_html(html_content)
    for name in names:
        try:
            if default_storage.exists(name):
                default_storage.delete(name)
                logger.info("Deleted content image from storage: %s", name)
        except Exception:
            logger.exception(
                "Error deleting content image from storage: %s", name
            )


# ===========================================================================
# BlogPost signals
# ===========================================================================

@receiver(post_delete, sender=BlogPost)
def delete_blog_post_files(sender, instance, **kwargs):
    """
    Triggered AFTER a BlogPost is deleted from the database.

    Deletes:
      1. The thumbnail image (if any).
      2. All inline images embedded in the CKEditor content body.
    """
    # 1. Delete the thumbnail via the field's own storage backend
    _delete_file(instance.thumbnail_image)

    # 2. Delete all CKEditor-embedded images from storage
    _delete_content_images(instance.content)


@receiver(pre_save, sender=BlogPost)
def delete_old_blog_post_files(sender, instance, **kwargs):
    """
    Triggered BEFORE a BlogPost is saved (i.e. on update, not on create).

    Compares the new field values against the existing database row and
    deletes any files that have been replaced or removed.

    Handles:
      1. Thumbnail replaced → old thumbnail deleted.
      2. Content images removed from the editor → orphaned images deleted.
    """
    if not instance.pk:
        return  # New object — nothing to clean up

    try:
        old_instance = BlogPost.objects.get(pk=instance.pk)
    except BlogPost.DoesNotExist:
        return  # Record was deleted between the check and now

    # 1. Has the thumbnail been swapped for a different file?
    if (
        old_instance.thumbnail_image
        and old_instance.thumbnail_image.name != getattr(instance.thumbnail_image, "name", None)
    ):
        _delete_file(old_instance.thumbnail_image)

    # 2. Find images that existed in the old content but are gone in the new content
    old_image_names = set(_extract_storage_names_from_html(old_instance.content))
    new_image_names = set(_extract_storage_names_from_html(instance.content))
    removed_names = old_image_names - new_image_names

    from django.core.files.storage import default_storage  # lazy import

    for name in removed_names:
        try:
            if default_storage.exists(name):
                default_storage.delete(name)
                logger.info(
                    "Deleted removed content image from storage: %s", name
                )
        except Exception:
            logger.exception(
                "Error deleting removed content image: %s", name
            )


# ===========================================================================
# HeroSection signals
# ===========================================================================

@receiver(post_delete, sender=HeroSection)
def delete_hero_section_files(sender, instance, **kwargs):
    """
    Triggered AFTER a HeroSection record is deleted.
    Deletes the hero background image from storage.
    """
    _delete_file(instance.hero_image)


@receiver(pre_save, sender=HeroSection)
def delete_old_hero_files(sender, instance, **kwargs):
    """
    Triggered BEFORE a HeroSection is saved.
    If the hero image has been replaced, deletes the old one from storage.
    """
    if not instance.pk:
        return

    try:
        old_instance = HeroSection.objects.get(pk=instance.pk)
    except HeroSection.DoesNotExist:
        return

    if (
        old_instance.hero_image
        and old_instance.hero_image.name != getattr(instance.hero_image, "name", None)
    ):
        _delete_file(old_instance.hero_image)
