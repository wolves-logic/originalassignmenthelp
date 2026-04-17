"""
URL configuration for orignalassignmenthelp project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Original Assignment Help Administration"
admin.site.site_title = "OAH Admin Portal"
admin.site.index_title = "Welcome to Original Assignment Help Dashboard"

urlpatterns = [
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("", include("Main.urls")),
    path("admin/", admin.site.urls),
]

# Serve uploaded media files in development.
# In production (USE_S3=True), media is served directly from S3 — this block
# is intentionally skipped because MEDIA_ROOT is not defined in that mode.
if settings.DEBUG and not getattr(settings, "USE_S3", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "Main.views.page_not_found"
handler500 = "Main.views.server_error"