from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
import os


class OfferBanner(models.Model):
    text = CKEditor5Field(config_name="offer_config", help_text="Offer text (Bold supported)")
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Offer Banner"
        verbose_name_plural = "Offer Banners"

    def __str__(self):
        # CKEditor5Field returns HTML — don't expose it as the string representation
        status = "Active" if self.is_active else "Inactive"
        return f"Offer Banner #{self.pk} ({status})"


class HeroSection(models.Model):
    badge_text = models.CharField(max_length=100, help_text="Top badge text")
    title_leading = models.CharField(max_length=200, help_text="First part of title (White)")
    title_highlight = models.CharField(max_length=200, help_text="Highlighted part of title (Color)")
    subtitle = models.TextField()
    hero_image = models.ImageField(upload_to="hero/", blank=True, null=True, help_text="Background image")
    button_1_text = models.CharField(max_length=50)
    button_2_text = models.CharField(max_length=50)
    stat_1_number = models.CharField(max_length=20)
    stat_1_label = models.CharField(max_length=50)
    stat_2_number = models.CharField(max_length=20)
    stat_2_label = models.CharField(max_length=50)
    stat_3_number = models.CharField(max_length=20)
    stat_3_label = models.CharField(max_length=50)
    stat_4_number = models.CharField(max_length=20)
    stat_4_label = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return "Hero Section Settings"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="URL-friendly version of the title")
    author = models.CharField(max_length=100, default="Admin")
    summary = models.TextField(
        help_text="Short summary for list view and SEO meta description", default=""
    )
    content = CKEditor5Field(config_name="blog_config", help_text="Blog content")
    thumbnail_image = models.ImageField(upload_to="blog_thumbnails/", blank=True, null=True)
    category = models.CharField(max_length=100, default="General", db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Service(models.Model):
    title = models.CharField(max_length=200, help_text="H1: Professional Essay Writing Service")
    slug = models.SlugField(unique=True)
    hero_image = models.ImageField(upload_to="services/hero/", help_text="Mandatory Hero Banner")
    thumbnail = models.ImageField(
        upload_to="services/thumbnails/", blank=True, null=True, help_text="For list view"
    )
    intro_description = models.TextField(help_text="Intro (2–3 lines — definition style)")
    content = CKEditor5Field(
        config_name="blog_config", help_text="Main content with H2s, H3s, images, etc."
    )
    is_active = models.BooleanField(default=True, db_index=True)
    show_in_menu = models.BooleanField(
        default=False, db_index=True, help_text="Show in navigation menu (Max 5 recommended)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Subject(models.Model):
    title = models.CharField(max_length=200, help_text="H1: Subject Name")
    slug = models.SlugField(unique=True)
    hero_image = models.ImageField(upload_to="subjects/hero/", help_text="Mandatory Hero Banner")
    thumbnail = models.ImageField(
        upload_to="subjects/thumbnails/", blank=True, null=True, help_text="For list view"
    )
    intro_description = models.TextField(help_text="Intro (2–3 lines — definition style)")
    content = CKEditor5Field(
        config_name="blog_config", help_text="Main content with H2s, H3s, images, etc."
    )
    is_active = models.BooleanField(default=True, db_index=True)
    show_in_menu = models.BooleanField(
        default=False, db_index=True, help_text="Show in navigation menu (Max 5 recommended)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=200, default="Privacy Policy")
    content = CKEditor5Field(config_name="blog_config", help_text="Privacy Policy Content")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Privacy Policy"

    def __str__(self):
        return self.title


class TermsCondition(models.Model):
    title = models.CharField(max_length=200, default="Terms & Conditions")
    content = CKEditor5Field(config_name="blog_config", help_text="Terms & Conditions Content")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Terms & Conditions"

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    student_name = models.CharField(max_length=100, help_text="Student's name")
    student_initials = models.CharField(max_length=5, default="AB", help_text="2-3 letter initials for avatar")
    course_field = models.CharField(max_length=100, help_text="e.g., Business Management, Computer Science")
    rating = models.IntegerField(
        default=5, 
        help_text="Rating out of 5",
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    message = models.TextField(help_text="Testimonial message")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Show on homepage")
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return f"{self.student_name} - {self.course_field}"


class FAQ(models.Model):
    question = models.CharField(max_length=300, help_text="FAQ question")
    answer = models.TextField(help_text="FAQ answer")
    is_active = models.BooleanField(default=True, db_index=True, help_text="Show on homepage")
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class CTABanner(models.Model):
    title = models.CharField(max_length=200, help_text="Main heading")
    subtitle = models.TextField(help_text="Subtitle text")
    button_text = models.CharField(max_length=50, help_text="CTA button text")
    button_link = models.CharField(max_length=200, help_text="Button link URL")
    feature_1 = models.CharField(max_length=100, help_text="First feature")
    feature_2 = models.CharField(max_length=100, help_text="Second feature")
    feature_3 = models.CharField(max_length=100, help_text="Third feature")
    guarantee_title = models.CharField(max_length=100, help_text="Guarantee badge title")
    guarantee_subtitle = models.CharField(max_length=100, help_text="Guarantee badge subtitle")
    is_active = models.BooleanField(default=True, help_text="Show on homepage")

    class Meta:
        verbose_name = "CTA Banner"
        verbose_name_plural = "CTA Banner"

    def __str__(self):
        return self.title


class AboutPage(models.Model):
    hero_bg_image = models.ImageField(
        upload_to="about/hero/", blank=True, null=True, help_text="Background image for the header"
    )
    story_badge = models.CharField(max_length=50, help_text="Badge text above heading")
    story_title = models.CharField(max_length=200)
    story_lead = models.TextField()
    story_description = models.TextField()
    story_image = models.ImageField(
        upload_to="about/", blank=True, null=True, help_text="Story section image"
    )
    timeline_title = models.CharField(max_length=100, default="Our Journey")
    timeline_description = models.TextField(default="Key milestones in our story.")
    vision_title = models.CharField(max_length=100)
    vision_text = models.TextField()
    mission_title = models.CharField(max_length=100)
    mission_text = models.TextField()
    company_name = models.CharField(max_length=200)
    company_legal_name = models.CharField(max_length=200)
    company_description = models.TextField()
    headquarters_location = models.CharField(max_length=200)
    students_helped = models.CharField(max_length=20)
    success_rate = models.CharField(max_length=20)
    years_experience = models.CharField(max_length=20)
    featured_image = models.ImageField(
        upload_to="about/featured/", blank=True, null=True,
        help_text="Large full-width image for the middle section",
    )
    featured_image_title = models.CharField(
        max_length=200, default="Global Impact", help_text="Title overlay for the image"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return "About Page Content"


class CoreValue(models.Model):
    title = models.CharField(max_length=100, help_text="e.g., Excellence, Integrity")
    description = models.TextField(help_text="Short description of this value")
    icon_class = models.CharField(
        max_length=50, default="bi-award", help_text="Bootstrap icon class (e.g., bi-award)"
    )
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.title


class Milestone(models.Model):
    year = models.CharField(max_length=10, help_text='e.g., 2014, Present')
    title = models.CharField(max_length=200)
    description = models.TextField()
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.year} - {self.title}"


class Guide(models.Model):
    title = models.CharField(max_length=200, help_text="Guide title")
    description = models.TextField(help_text="Short description")
    pdf_file = models.FileField(
        upload_to="guides/",
        help_text="Upload PDF file (Optional if Link provided)",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf"])],
    )
    external_link = models.URLField(
        blank=True, null=True, help_text="Or provide a direct link (e.g. Google Drive)"
    )
    icon_class = models.CharField(
        max_length=50, default="bi-journal-richtext", help_text="Bootstrap icon class"
    )
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class Tool(models.Model):
    title = models.CharField(max_length=200, help_text="Tool name")
    description = models.TextField(help_text="What this tool does")
    external_link = models.URLField(help_text="External tool URL")
    icon_class = models.CharField(
        max_length=50, default="bi-tools", help_text="Bootstrap icon class"
    )
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class SampleWork(models.Model):
    title = models.CharField(max_length=200, help_text="Sample work title")
    description = models.TextField(help_text="Brief description")
    category = models.CharField(max_length=100, help_text="e.g., Essay, Case Study, Research Paper")
    academic_level = models.CharField(max_length=50, help_text="e.g., MBA, Undergraduate, PhD")
    file = models.FileField(
        upload_to="sample_works/",
        help_text="Upload sample file (PDF, DOCX, DOC, ZIP)",
        validators=[FileExtensionValidator(["pdf", "docx", "doc", "zip"])],
    )
    file_type = models.CharField(max_length=10, default="PDF", help_text="PDF, DOC, ZIP, etc.")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Sample Work"
        verbose_name_plural = "Sample Works"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Derive file_type from the uploaded file's extension so the
        # admin never needs to set it manually.
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            self.file_type = {
                ".pdf": "PDF",
                ".doc": "DOC",
                ".docx": "DOC",
                ".zip": "ZIP",
                ".ppt": "PPT",
                ".pptx": "PPT",
                ".xls": "XLS",
                ".xlsx": "XLS",
            }.get(ext, "FILE")
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    site_description = models.TextField(help_text="Footer description text")
    email = models.EmailField(help_text="Contact email")
    phone = models.CharField(max_length=20, help_text="Contact phone number")
    whatsapp_number = models.CharField(max_length=20, help_text="WhatsApp number")
    head_office_address = models.TextField(help_text="Head Office Address")
    branch_office_address = models.TextField(help_text="Branch Office Address")
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    copyright_text = models.CharField(
        max_length=255,
        default="© 2014 originalassignmenthelp.com - Operated by Harviera IT Solutions",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Configuration"

    def clean(self):
        # Enforce singleton — only one SiteSettings record should ever exist.
        # Django Admin calls full_clean() before save, so this surfaces as a
        # proper validation error rather than silently doing nothing.
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(
                "Only one Site Settings record is allowed. "
                "Please edit the existing one instead of creating a new one."
            )

    # Removed def save(self, *args, **kwargs) which called self.full_clean().
    # Calling full_clean() unconditionally in save() causes crashes in loaddata 
    # fixtures and background scripting because ValidationErrors aren't expected there.


class ContactPage(models.Model):
    hero_title = models.CharField(max_length=200, default="Get in Touch")
    hero_subtitle = models.TextField(
        default="Have questions? We're here to help! Reach out to our support team anytime."
    )
    whatsapp_title = models.CharField(max_length=200, default="Chat on WhatsApp")
    whatsapp_subtitle = models.CharField(max_length=200, default="Available 24/7 for instant replies.")
    whatsapp_number = models.CharField(max_length=20, default="919959691347")
    whatsapp_response_time = models.CharField(max_length=100, default="< 2 minutes")
    email_title = models.CharField(max_length=200, default="Email Support")
    email_description = models.CharField(max_length=200, default="For detailed inquiries or attachments.")
    email_address = models.EmailField(default="support@academichelp.com")
    head_office_title = models.CharField(max_length=200, default="Head Office")
    head_office_address = models.TextField(
        default="Old GT Rd, Gandhi Ashram Colony, Palwal, India, 121102"
    )
    branch_office_title = models.CharField(max_length=200, default="Branch Office")
    branch_office_address = models.TextField(
        default="Near Kamineni Hospital, LB Nagar, Hyderabad, Telangana, India - 500074"
    )
    map_embed_url = models.URLField(max_length=1000, help_text="Google Maps embed URL for Head Office")
    branch_map_embed_url = models.URLField(
        max_length=1000, blank=True, help_text="Google Maps embed URL for Branch Office"
    )
    map_overlay_text = models.TextField(
        default="We are located centrally in Palwal. Drop by for a coffee and consultation."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contact Page"
        verbose_name_plural = "Contact Page"

    def __str__(self):
        return "Contact Page Settings"


class RefundPolicy(models.Model):
    title = models.CharField(max_length=200, default="Refund & Money-Back Guarantee Policy")
    content = CKEditor5Field(config_name="blog_config", help_text="Refund Policy Content")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Refund Policy"

    def __str__(self):
        return self.title
