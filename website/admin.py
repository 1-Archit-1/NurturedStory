from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    ContactSubmission,
    LicensurePage,
    ResourceCategory,
    ResourceLink,
    Service,
    SessionRate,
    SiteSettings,
    TherapistProfile,
    Training,
)


# ---------------------------------------------------------------------------
# Singleton admin — hides the 'Add' button and goes straight to the edit form
# ---------------------------------------------------------------------------

class SingletonModelAdmin(admin.ModelAdmin):
    """
    Admin base for models that should only ever have one row.
    Clicking the section in the admin sidebar takes you straight to the
    edit form rather than a list page.
    """

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def changelist_view(self, request, extra_context=None):
        # Auto-create the singleton row if it doesn't exist yet, then redirect
        obj = self.model.load()
        app = self.model._meta.app_label
        model = self.model._meta.model_name
        return HttpResponseRedirect(reverse(f"admin:{app}_{model}_change", args=[obj.pk]))


# ---------------------------------------------------------------------------
# Site Settings
# Edits: practice name, tagline, about-the-practice blurb (home page),
#        contact phone + email (pricing page + footer),
#        sliding scale note (pricing page), footer copyright line
# ---------------------------------------------------------------------------

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    fieldsets = [
        # Affects: home page hero, header brand name, footer brand name
        ("Practice Info", {
            "fields": ["practice_name", "tagline", "about_practice"],
        }),
        # Affects: pricing page 'Reach Out Directly' card, footer, trainings mailto link
        ("Contact Details", {
            "fields": ["phone", "email"],
        }),
        # Affects: pricing page, shown beneath the session rate rows
        ("Pricing Page", {
            "fields": ["sliding_scale_note"],
        }),
        # Affects: copyright line at the bottom of every page
        ("Footer", {
            "fields": ["footer_text"],
        }),
    ]


# ---------------------------------------------------------------------------
# Therapist Profile
# Edits: 'About Shel Pohnan' card on the home page —
#        name, credentials subtitle, bio paragraphs, profile photo
# ---------------------------------------------------------------------------

@admin.register(TherapistProfile)
class TherapistProfileAdmin(SingletonModelAdmin):
    fieldsets = [
        # Affects: card heading and credentials line under the name
        ("Identity", {
            "fields": ["name", "credentials", "photo"],
        }),
        # Affects: the body paragraphs in the teal 'About' card
        ("Bio", {
            "fields": ["bio"],
        }),
    ]


# ---------------------------------------------------------------------------
# Services
# Edits: bullet point list in the 'Services' card at the bottom of the home page
#        Use 'order' to resequence items, toggle 'is_active' to hide without deleting
# ---------------------------------------------------------------------------

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["label", "order", "is_active"]
    list_editable = ["order", "is_active"]
    ordering = ["order"]


# ---------------------------------------------------------------------------
# Session Rates
# Edits: each rate row in the purple 'Session Rates' card on the pricing page
#        (e.g. 'Individual Session — $150 / 50 min', 'Couples Session — $200 / 80 min')
# ---------------------------------------------------------------------------

@admin.register(SessionRate)
class SessionRateAdmin(admin.ModelAdmin):
    list_display = ["session_type", "duration_minutes", "price", "order", "is_active"]
    list_editable = ["price", "duration_minutes", "order", "is_active"]
    ordering = ["order"]
    fieldsets = [
        (None, {
            "fields": ["session_type", "duration_minutes", "price", "note", "order", "is_active"],
        }),
        ("Contact Form Integration", {
            "description": (
                "This message is pre-filled in the contact form when a visitor "
                "clicks the 'Book' button on this rate row. Leave blank to use "
                "the default message."
            ),
            "fields": ["booking_message"],
        }),
    ]


# ---------------------------------------------------------------------------
# Resource Categories + Links
# Edits: the category cards on the Resources page and the links inside each modal
#        - Category: card title, emoji, intro description shown at top of modal
#        - Links (inline): each link title, URL, and description shown in the modal list
# ---------------------------------------------------------------------------

class ResourceLinkInline(admin.TabularInline):
    """
    Inline link editor inside a ResourceCategory.
    Each row = one link shown in the modal when that category card is clicked.
    """
    model = ResourceLink
    extra = 1
    fields = ["title", "url", "file", "description", "order", "is_active"]
    ordering = ["order"]


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "emoji", "order", "is_active"]
    list_editable = ["order", "is_active"]
    ordering = ["order"]
    inlines = [ResourceLinkInline]
    fieldsets = [
        # Affects: card face on the resources grid + modal heading/intro
        (None, {
            "fields": ["name", "emoji", "description", "order", "is_active"],
        }),
    ]


# ---------------------------------------------------------------------------
# Trainings
# Edits: training cards on the Trainings page
#        When no trainings are published, the page shows 'None currently available'
# ---------------------------------------------------------------------------

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ["title", "date", "order", "is_published"]
    list_editable = ["order", "is_published"]
    ordering = ["order", "date"]
    fieldsets = [
        # Affects: training card heading, body text, date, and sign-up button
        (None, {
            "fields": ["title", "description", "date", "signup_url", "order", "is_published"],
        }),
    ]


# ---------------------------------------------------------------------------
# Licensure Page
# Edits: all text content on the /licensure/ page — both cards + disclaimer
# ---------------------------------------------------------------------------

@admin.register(LicensurePage)
class LicensurePageAdmin(SingletonModelAdmin):
    fieldsets = [
        ("Page Header", {
            "fields": ["page_title", "page_lede"],
        }),
        ("Licensure Consultation Card", {
            "fields": ["consult_intro", "consult_items", "consult_rate_label", "consult_rate"],
        }),
        ("CE Renewal Card", {
            "fields": ["renewal_intro", "renewal_rate_label", "renewal_rate"],
        }),
        ("Disclaimer", {
            "fields": ["disclaimer"],
        }),
    ]


# ---------------------------------------------------------------------------
# Contact Submissions
# Edits: read-only inbox of messages from the 'Send a Message' form on the pricing page
#        Toggle 'is_read' to track which messages have been seen
#        No add permission — submissions come from the public form only
# ---------------------------------------------------------------------------

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "submitted_at", "is_read"]
    list_editable = ["is_read"]
    list_filter = ["is_read"]
    readonly_fields = ["name", "email", "phone", "message", "submitted_at"]
    ordering = ["-submitted_at"]

    def has_add_permission(self, request):
        return False  # Submissions come from the public contact form only

    def has_delete_permission(self, request, obj=None):
        return True  # Allow cleaning up old submissions
