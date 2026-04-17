"""
views.py
--------
Refactored to use Class-Based Views (CBVs) and custom caching mixins,
making the code DRY and robust.

All views implement a Redis cache-aside pattern:
    Request → cache.get(key) → HIT  → render template (0 DB queries)
                             → MISS → query DB → cache.set() → render

Search views are intentionally not cached based on user inputs.
"""

import logging
import os
import random

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, View

from .cache_utils import (
    key_home, key_blog_categories, key_blog_detail,
    key_service_list, key_service_detail,
    key_subject_list, key_subject_detail,
    key_about, key_contact,
    key_privacy, key_terms, key_refund,
    TTL_HOME, TTL_DETAIL, TTL_LIST, TTL_CATEGORIES, TTL_STATIC, TTL_ABOUT,
)
from .models import (
    HeroSection, BlogPost, Service, Subject,
    PrivacyPolicy, TermsCondition, Testimonial, FAQ,
    CTABanner, AboutPage, CoreValue, Milestone,
    Guide, Tool, SampleWork, ContactPage, RefundPolicy,
)
from .mixins import CacheListMixin, CacheDetailMixin, CacheTemplateMixin

logger = logging.getLogger(__name__)


# ===========================================================================
# Home
# ===========================================================================

class HomeView(CacheTemplateMixin, TemplateView):
    template_name = "Main/home.html"
    cache_key_func = staticmethod(key_home)
    cache_timeout = TTL_HOME

    def build_context_data(self, **kwargs):
        # Fallback dictionary evaluation
        return {
            "hero": HeroSection.objects.order_by('pk').last(),
            "services": list(Service.objects.filter(is_active=True)[:6]),
            "subjects": list(Subject.objects.filter(is_active=True)[:6]),
            "testimonials": list(Testimonial.objects.filter(is_active=True)),
            "faqs": list(FAQ.objects.filter(is_active=True)[:10]),
            "cta_banner": CTABanner.objects.filter(is_active=True).last(),
            "recent_tools": list(Tool.objects.filter(is_active=True).order_by('display_order')[:3]),
            "recent_samples": list(SampleWork.objects.filter(is_active=True).order_by('-created_at')[:3]),
            "recent_guides": list(Guide.objects.filter(is_active=True).order_by('-created_at')[:3]),
        }


# ===========================================================================
# Blog
# ===========================================================================

class BlogListView(ListView):
    template_name = "Main/blogs/blog.html"
    context_object_name = "page_obj"
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get("q")
        category = self.request.GET.get("category")
        blogs = BlogPost.objects.filter(is_published=True).order_by('-created_at')

        if query:
            blogs = blogs.filter(
                Q(title__icontains=query) | Q(summary__icontains=query) | Q(category__icontains=query)
            )
        if category:
            blogs = blogs.filter(category=category)
        return blogs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Cache the categories list — same for every visitor
        categories = cache.get(key_blog_categories())
        if categories is None:
            categories = list(
                BlogPost.objects.filter(is_published=True)
                .values_list('category', flat=True)
                .distinct().order_by('category')
            )
            cache.set(key_blog_categories(), categories, timeout=TTL_CATEGORIES)

        context["query"] = self.request.GET.get("q")
        context["categories"] = categories
        context["selected_category"] = self.request.GET.get("category")
        return context


class BlogDetailView(CacheDetailMixin, DetailView):
    template_name = "Main/blogs/blog_page.html"
    context_object_name = "post"
    cache_timeout = TTL_DETAIL

    def get_cache_key(self, slug):
        return key_blog_detail(slug)

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Random related posts are evaluated fresh intentionally
        context["related_posts"] = BlogPost.objects.filter(
            category=post.category, is_published=True
        ).exclude(id=post.id)[:3]

        categories = cache.get(key_blog_categories())
        if categories is None:
            categories = list(BlogPost.objects.filter(is_published=True).values_list('category', flat=True).distinct().order_by('category'))
            cache.set(key_blog_categories(), categories, timeout=TTL_CATEGORIES)
        context["categories"] = categories

        return context


# ===========================================================================
# Services
# ===========================================================================

class ServiceListView(CacheListMixin, ListView):
    template_name = "Main/services/service_list.html"
    context_object_name = "page_obj"
    paginate_by = 12
    cache_timeout = TTL_LIST

    def get_cache_key(self):
        return key_service_list()

    def get_queryset(self):
        return Service.objects.filter(is_active=True)


class ServiceDetailView(CacheDetailMixin, DetailView):
    template_name = "Main/services/service_detail.html"
    context_object_name = "service"
    cache_timeout = TTL_DETAIL

    def get_cache_key(self, slug):
        return key_service_detail(slug)

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ids = list(Service.objects.filter(is_active=True).exclude(id=self.object.id).values_list("id", flat=True))
        context["related_services"] = Service.objects.filter(id__in=random.sample(ids, min(3, len(ids)))) if ids else []
        return context


# ===========================================================================
# Subjects
# ===========================================================================

class SubjectListView(CacheListMixin, ListView):
    template_name = "Main/subjects/subject_list.html"
    context_object_name = "page_obj"
    paginate_by = 12
    cache_timeout = TTL_LIST

    def get_cache_key(self):
        return key_subject_list()

    def get_queryset(self):
        return Subject.objects.filter(is_active=True)


class SubjectDetailView(CacheDetailMixin, DetailView):
    template_name = "Main/subjects/subject_detail.html"
    context_object_name = "subject"
    cache_timeout = TTL_DETAIL

    def get_cache_key(self, slug):
        return key_subject_detail(slug)

    def get_queryset(self):
        return Subject.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ids = list(Subject.objects.filter(is_active=True).exclude(id=self.object.id).values_list("id", flat=True))
        context["related_subjects"] = Subject.objects.filter(id__in=random.sample(ids, min(3, len(ids)))) if ids else []
        return context


# ===========================================================================
# Static / policy pages
# ===========================================================================

class PrivacyPolicyView(CacheTemplateMixin, TemplateView):
    template_name = "Main/privacy_policy.html"
    cache_key_func = staticmethod(key_privacy)
    cache_timeout = TTL_STATIC

    def build_context_data(self, **kwargs):
        return {"policy": PrivacyPolicy.objects.last()}


class TermsConditionsView(CacheTemplateMixin, TemplateView):
    template_name = "Main/terms_conditions.html"
    cache_key_func = staticmethod(key_terms)
    cache_timeout = TTL_STATIC

    def build_context_data(self, **kwargs):
        return {"terms": TermsCondition.objects.last()}


class RefundPolicyView(CacheTemplateMixin, TemplateView):
    template_name = "Main/refund_policy.html"
    cache_key_func = staticmethod(key_refund)
    cache_timeout = TTL_STATIC

    def build_context_data(self, **kwargs):
        return {"refund_policy": RefundPolicy.objects.first()}


# ===========================================================================
# About & Contact
# ===========================================================================

class AboutView(CacheTemplateMixin, TemplateView):
    template_name = "Main/about.html"
    cache_key_func = staticmethod(key_about)
    cache_timeout = TTL_ABOUT

    def build_context_data(self, **kwargs):
        return {
            "about_page": AboutPage.objects.filter(is_active=True).last(),
            "core_values": list(CoreValue.objects.filter(is_active=True)),
            "milestones": list(Milestone.objects.filter(is_active=True)),
        }


class ContactView(CacheTemplateMixin, TemplateView):
    template_name = "Main/contact.html"
    cache_key_func = staticmethod(key_contact)
    cache_timeout = TTL_ABOUT

    def build_context_data(self, **kwargs):
        return {"contact_page": ContactPage.objects.first()}


# ===========================================================================
# Resources (search-driven — not cached at the view level)
# ===========================================================================

class ResourcesHubView(TemplateView):
    template_name = "Main/resources/resources.html"

    def get_context_data(self, **kwargs):
        return {
            "guides_count": Guide.objects.filter(is_active=True).count(),
            "tools_count": Tool.objects.filter(is_active=True).count(),
            "works_count": SampleWork.objects.filter(is_active=True).count(),
        }


class GuideListView(ListView):
    template_name = "Main/resources/guides.html"
    context_object_name = "page_obj"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = Guide.objects.filter(is_active=True)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        return context


class ToolListView(ListView):
    template_name = "Main/resources/tools.html"
    context_object_name = "page_obj"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        qs = Tool.objects.filter(is_active=True)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        return context


class SampleWorkListView(ListView):
    template_name = "Main/resources/works.html"
    context_object_name = "page_obj"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        level = self.request.GET.get('level')
        qs = SampleWork.objects.filter(is_active=True)

        if query:
            qs = qs.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)
            )
        if category:
            qs = qs.filter(category=category)
        if level:
            qs = qs.filter(academic_level=level)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = list(SampleWork.objects.filter(is_active=True).values_list('category', flat=True).distinct())
        context["levels"] = list(SampleWork.objects.filter(is_active=True).values_list('academic_level', flat=True).distinct())
        context["query"] = self.request.GET.get("q")
        context["selected_category"] = self.request.GET.get("category")
        context["selected_level"] = self.request.GET.get("level")
        return context


# ===========================================================================
# File download
# ===========================================================================

class DownloadSampleView(View):
    def get(self, request, sample_id, *args, **kwargs):
        try:
            sample = SampleWork.objects.get(pk=sample_id, is_active=True)
        except SampleWork.DoesNotExist:
            raise Http404("Sample not found")

        if not sample.file:
            raise Http404("File record not found")

        # S3 / remote storage: redirect to URL
        if getattr(settings, "USE_S3", False):
            return HttpResponseRedirect(sample.file.url)

        # Local filesystem: stream as attachment
        try:
            file_path = sample.file.path
            if not os.path.exists(file_path):
                raise Http404("File missing on server")
                
            return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))
        except Http404:
            raise
        except Exception:
            logger.exception("Error streaming sample file pk=%s", sample_id)
            raise Http404("Error accessing file")


# ===========================================================================
# Status and Error Handlers
# ===========================================================================

def health_check(request):
    """Simple 200 OK view for load balancers and Docker health checks."""
    return JsonResponse({"status": "ok"})


def page_not_found(request, exception):
    from .processor import global_context
    context = global_context(request)
    return render(request, "404.html", context, status=404)


def server_error(request):
    return render(request, "500.html", status=500)

