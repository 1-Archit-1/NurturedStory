"""
Template context processors.

Anything registered here is automatically available in every template
without needing to pass it explicitly from each view.
"""
from .models import SiteSettings


def site_settings(request):
    """
    Makes `site` (the SiteSettings singleton) available globally in templates.
    Used by base.html for the footer, title, and other shared elements.
    """
    return {"site": SiteSettings.load()}
