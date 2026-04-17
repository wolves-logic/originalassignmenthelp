"""
storage_backends.py
-------------------
Custom Django storage backends for Amazon S3.

This module defines two storage classes:
  - MediaStorage  : All user-uploaded files (images, PDFs, etc.)

Both classes extend S3Boto3Storage from django-storages and customise
the S3 key prefix (location), so files are neatly organised inside
the bucket under:

    <bucket>/
    └── media/           ← MediaStorage uploads land here
        ├── hero/
        ├── blog_thumbnails/
        ├── services/
        ├── subjects/
        ├── guides/
        ├── sample_works/
        ├── about/
        └── uploads/     ← CKEditor inline images

Usage: configured via STORAGES["default"] in settings.py.
"""

from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Storage backend for all user-uploaded media files.

    Files are stored under the 'media/' prefix inside the S3 bucket.
    When Django resolves a FileField/ImageField URL, it prepends
    MEDIA_URL automatically (already set to the S3 base URL in settings).
    """

    # All media files live under this prefix in the bucket.
    location = "media"

    # Never silently overwrite an existing file: always generate a
    # unique name if a file with the same name already exists.
    file_overwrite = False
