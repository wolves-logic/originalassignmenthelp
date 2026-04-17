from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("blog/", views.BlogListView.as_view(), name="blog_list"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog_detail"),
    path("services/", views.ServiceListView.as_view(), name="service_list"),
    path("services/<slug:slug>/", views.ServiceDetailView.as_view(), name="service_detail"),
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/<slug:slug>/", views.SubjectDetailView.as_view(), name="subject_detail"),
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms-conditions/", views.TermsConditionsView.as_view(), name="terms_conditions"),
    path("refund-policy/", views.RefundPolicyView.as_view(), name="refund_policy"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("resources/", views.ResourcesHubView.as_view(), name="resources"),
    path("resources/guides/", views.GuideListView.as_view(), name="guides"),
    path("resources/tools/", views.ToolListView.as_view(), name="tools"),
    path("resources/works/", views.SampleWorkListView.as_view(), name="works"),
    path("resources/works/download/<int:sample_id>/", views.DownloadSampleView.as_view(), name="download_sample"),
    path("health/", views.health_check, name="health_check"),
]
