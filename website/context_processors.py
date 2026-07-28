"""
Template context processors.

Anything registered here is automatically available in every template
without needing to pass it explicitly from each view.
"""
from django.conf import settings
from .models import LocalBusinessSEO, SiteSettings


def site_settings(request):
    """
    Makes `site`, `seo`, and `SITE_URL` available globally in templates.
    Used by base.html for footer, title, canonical tags, structured data, etc.
    """
    return {
        "site": SiteSettings.load(),
        "local_seo": LocalBusinessSEO.load(),
        "SITE_URL": settings.SITE_URL,
    }
