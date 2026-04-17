from django.contrib import admin
from .models import OfferBanner, HeroSection, BlogPost, Service, Subject, PrivacyPolicy, TermsCondition, Testimonial, FAQ, CTABanner, AboutPage, CoreValue, Milestone, Guide, Tool, SampleWork, SiteSettings, ContactPage, RefundPolicy

class SingletonModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(OfferBanner)
class OfferBannerAdmin(SingletonModelAdmin):
    list_display = ("text", "is_active", "created_at")

@admin.register(HeroSection)
class HeroSectionAdmin(SingletonModelAdmin):
    list_display = ("__str__",)



@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'show_in_menu', 'created_at')
    list_filter = ('is_active', 'show_in_menu', 'created_at')
    search_fields = ('title', 'intro_description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'show_in_menu')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'show_in_menu', 'created_at')
    list_filter = ('is_active', 'show_in_menu', 'created_at')
    search_fields = ('title', 'intro_description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'show_in_menu')

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(SingletonModelAdmin):
    list_display = ('title', 'updated_at')

@admin.register(TermsCondition)
class TermsConditionAdmin(SingletonModelAdmin):
    list_display = ('title', 'updated_at')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'course_field', 'rating', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'rating', 'created_at')
    search_fields = ('student_name', 'course_field', 'message')
    list_editable = ('is_active', 'display_order')

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('question', 'answer')
    list_editable = ('is_active', 'display_order')

@admin.register(CTABanner)
class CTABannerAdmin(SingletonModelAdmin):
    list_display = ('title', 'is_active')
    list_editable = ('is_active',)

@admin.register(AboutPage)
class AboutPageAdmin(SingletonModelAdmin):
    list_display = ('__str__', 'is_active')
    fieldsets = (
        ('Hero Section', {'fields': ('hero_bg_image',)}),
        ('Story Section', {'fields': ('story_title', 'story_lead', 'story_description', 'story_image')}),
        ('Timeline Section', {'fields': ('timeline_title', 'timeline_description')}),
        ('Vision & Mission', {'fields': ('vision_title', 'vision_text', 'mission_title', 'mission_text')}),
        ('Company Information', {'fields': ('company_name', 'company_legal_name', 'company_description', 'headquarters_location')}),
        ('Statistics', {'fields': ('students_helped', 'success_rate', 'years_experience')}),
        ('Featured Image Section', {'fields': ('featured_image', 'featured_image_title')}),
        ('Status', {'fields': ('is_active',)}),
    )

@admin.register(CoreValue)
class CoreValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active',)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active',)

@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'display_order', 'created_at')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('title', 'external_link', 'is_active', 'display_order', 'created_at')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')

@admin.register(SampleWork)
class SampleWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'academic_level', 'file_type', 'is_active', 'display_order', 'created_at')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active', 'category', 'academic_level', 'file_type', 'created_at')
    search_fields = ('title', 'description', 'category')

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    list_display = ("__str__", "email", "phone")
    fieldsets = (
        ('General Information', {
            'fields': ('site_description', 'copyright_text')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'whatsapp_number')
        }),
        ('Addresses', {
            'fields': ('head_office_address', 'branch_office_address')
        }),
        ('Social Media', {
            'fields': ('facebook_link', 'instagram_link', 'twitter_link', 'linkedin_link')
        }),
    )


@admin.register(ContactPage)
class ContactPageAdmin(SingletonModelAdmin):
    list_display = ('__str__', 'is_active')
    fieldsets = (
        ('Hero Section', {'fields': ('hero_title', 'hero_subtitle')}),
        ('WhatsApp Section', {'fields': ('whatsapp_title', 'whatsapp_subtitle', 'whatsapp_number', 'whatsapp_response_time')}),
        ('Email Support', {'fields': ('email_title', 'email_description', 'email_address')}),
        ('Office Locations', {'fields': ('head_office_title', 'head_office_address', 'branch_office_title', 'branch_office_address')}),
        ('Map', {'fields': ('map_embed_url', 'branch_map_embed_url', 'map_overlay_text')}),
        ('Status', {'fields': ('is_active',)}),
    )



@admin.register(RefundPolicy)
class RefundPolicyAdmin(SingletonModelAdmin):
    list_display = ('title', 'updated_at')
    fields = ('title', 'content')

