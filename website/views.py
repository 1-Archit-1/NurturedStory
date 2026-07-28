from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django_ratelimit.decorators import ratelimit

from .forms import ContactForm
from .models import (
    ContactSubmission,
    LicensurePage,
    LocalBusinessSEO,
    PageSEO,
    ResourceCategory,
    Service,
    SessionRate,
    SiteSettings,
    TherapistProfile,
    Training,
)


# ---------------------------------------------------------------------------
# Cosmic scene — unchanged, purely visual/layout concern
# ---------------------------------------------------------------------------

SOLAR_SYSTEM = [
    # Palette names are magic strings — must match in all three places:
    #   CSS:  .palette-{name}          → static/css/site.css  (base color + box-shadow)
    #   JS:   BAND_CONFIGS["{name}"]   → static/js/cosmic_scene.js  (SVG band definitions)
    {"id": "mercury", "label": "Mercury", "size": 34,  "palette": "slate"},
    {"id": "venus",   "label": "Venus",   "size": 40,  "palette": "rose"},
    {"id": "earth",   "label": "Earth",   "size": 45,  "palette": "blue"},
    {"id": "mars",    "label": "Mars",    "size": 39,  "palette": "champagne"},
    #{"id": "jupiter", "label": "Jupiter", "size": 160, "palette": "midnight"},
    {"id": "saturn",  "label": "Saturn",  "size": 119, "palette": "sage", "ring": True},
    {"id": "uranus",  "label": "Uranus",  "size": 84,  "palette": "dusk-teal"},
    {"id": "neptune", "label": "Neptune", "size": 69,  "palette": "violet"},
    {"id": "pluto",   "label": "Pluto",   "size": 17,  "palette": "slate"},
]


def build_scene(planets: list[dict], constellation_layout: str = "default") -> dict:
    return {
        "stars": 120,
        "constellation_layout": constellation_layout,
        "constellations": [
            {
                "id": "nurtured_story",
                "label": "Nurtured Story",
                "color": "rgba(200, 220, 255, 0.38)",
                # 0=spine top, 1=spine middle (binding), 2=spine bottom,
                # 3=left page top, 4=left page bottom,
                # 5=right page top, 6=right page bottom
                "points": [
                    {"x": 50, "y": 25},
                    {"x": 50, "y": 50},
                    {"x": 50, "y": 75},
                    {"x": 15, "y": 18},
                    {"x": 15, "y": 82},
                    {"x": 85, "y": 18},
                    {"x": 85, "y": 82},
                ],
            },
            {
                "id": "big_dipper",
                "label": "Big Dipper",
                "color": "rgba(180, 210, 255, 0.42)",
                # Bowl: 0=Phecda (bottom-left), 1=Merak (bottom-right),
                #       2=Dubhe (top-right, handle join),    3=Megrez (top-left)
                # Handle: 4=Alioth, 5=Mizar, 6=Alkaid (tip, upper-right)
                "points": [
                    {"x": 25, "y": 74},
                    {"x": 42, "y": 72},
                    {"x": 48, "y": 52},
                    {"x": 30, "y": 48},
                    {"x": 61, "y": 39},
                    {"x": 72, "y": 22},
                    {"x": 65, "y": 8},
                ],
            },
            {
                "id": "orion",
                "label": "Orion",
                "color": "rgba(168, 210, 255, 0.36)",
                # 0=Betelgeuse (left shoulder), 1=Bellatrix (right shoulder),
                # 2=Alnitak (belt left), 3=Alnilam (belt centre), 4=Mintaka (belt right),
                # 5=Saiph (left foot), 6=Rigel (right foot), 7=Meissa (head)
                "points": [
                    {"x": 10, "y": 15},
                    {"x": 35, "y": 20},
                    {"x": 20, "y": 50},
                    {"x": 30, "y": 55},
                    {"x": 40, "y": 50},
                    {"x": 10, "y": 95},
                    {"x": 55, "y": 90},
                    {"x": 25, "y": 5},
                ],
            },
            {
                "id": "canis_major",
                "label": "Canis Major",
                "color": "rgba(180, 210, 255, 0.32)",
                # Dog oriented diagonally — head top-right, body sweeping to bottom-left
                # 0=Sirius (head, brightest), 1=Mirzam (right of Sirius),
                # 2=Muliphein (left of Sirius), 3=neck/upper body,
                # 4=Wezen (lower body), 5=Adhara (hind, bright),
                # 6=Aludra (tail tip, bottom-left), 7=front leg/paw
                "points": [
                    {"x": 75, "y": 20}, #Sirius
                    {"x": 90, "y": 28}, #Mirzam
                    {"x": 60, "y": 15}, #Front leg
                    {"x": 54, "y": 10}, #Muliphein
                    {"x": 62, "y": 3}, #Head of dog
                    {"x": 60, "y": 45}, #Thanih al Adzari
                    {"x": 45, "y": 60},#Wezen
                    {"x": 28, "y": 72},#Aludra
                    {"x": 55, "y": 75},#Adhara
                    {"x": 80, "y": 80},#Furud
                ],
            },

        ],
        "planets": planets,
    }


def solar_planets(anchor_map: dict[str, str | None]) -> list[dict]:
    planets = []
    for index, planet in enumerate(SOLAR_SYSTEM):
        item = planet.copy()
        item["anchor"] = anchor_map.get(planet["id"])
        item["drift"] = index
        planets.append(item)
    return planets


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def home(request: HttpRequest) -> HttpResponse:
    context = {
        "active_page": "home",
        "page_seo": PageSEO.objects.filter(page="home").first(),
        "site": SiteSettings.load(),
        "therapist": TherapistProfile.load(),
        # Only active services, already ordered by `order` field
        "services": Service.objects.filter(is_active=True),
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    "venus": "profile-photo",
                    "earth": "profile-photo",
                    "mars": "about-practice",
                    "jupiter": "about-practice",
                    "saturn": "about-me",
                    "uranus": "about-me",
                    "neptune": None,
                }
            ),
            constellation_layout= 'home'
        ),
    }
    return render(request, "pages/home.html", context)


@ratelimit(key='ip', rate='5/h', method='POST', block=False)
def pricing(request: HttpRequest) -> HttpResponse:
    submitted = request.GET.get("submitted") == "1"
    rate_limited = getattr(request, 'limited', False)

    if request.method == "POST" and not rate_limited:
        form = ContactForm(request.POST)
        if form.is_valid():
            # Honeypot check — silently discard if the hidden field was filled
            if form.cleaned_data.get("website"):
                return redirect(f"{reverse('pricing')}?submitted=1")

            name    = form.cleaned_data["name"]
            email   = form.cleaned_data["email"]
            phone   = form.cleaned_data.get("phone", "")
            message = form.cleaned_data["message"]

            # Save to DB so it's visible in the admin
            ContactSubmission.objects.create(
                name=name,
                email=email,
                phone=phone,
                message=message,
            )

            # Send notification email
            phone_line = f"\nPhone: {phone}" if phone else ""
            try:
                send_mail(
                    subject=f"New message from {name} — Nurtured Story",
                    message=(
                        f"Name: {name}\n"
                        f"Email: {email}"
                        f"{phone_line}\n\n"
                        f"Message:\n{message}"
                    ),
                    from_email=settings.EMAIL_HOST_USER or "noreply@nurturedstory.com",
                    recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
                    fail_silently=False,
                )
            except Exception:
                # Don't let an email failure block the user's submission —
                # it's already saved to the DB.
                pass

            return redirect(f"{reverse('pricing')}?submitted=1")
    else:
        form = ContactForm()

    rates = list(SessionRate.objects.filter(is_active=True))

    # Build a plain Python list — the template's json_script filter will serialise it
    rates_data = [
        {
            "id": r.pk,
            "session_type": r.session_type,
            "duration_minutes": r.duration_minutes,
            "price": str(r.price),
            "booking_message": r.booking_message or (
                f"Hi, I'm interested in booking a {r.session_type} "
                f"({r.duration_minutes} min, ${int(r.price)}). "
                f"Please let me know your availability."
            ),
        }
        for r in rates
    ]

    context = {
        "active_page": "pricing",
        "page_seo": PageSEO.objects.filter(page="pricing").first(),
        "form": form,
        "submitted": submitted,
        "rate_limited": rate_limited,
        # Singleton — phone, email, sliding scale note
        "site": SiteSettings.load(),
        # Active session rates in display order
        "session_rates": rates,
        "session_rates_json": rates_data,
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    "venus": "session-rates",
                    "earth": "session-rates",
                    "mars": "direct-contact",
                    "jupiter": "session-rates",
                    "saturn": "contact-form",
                    "uranus": "contact-form",
                    "neptune": None,
                }
            ),
            constellation_layout= 'top-heavy'
        ),
    }
    return render(request, "pages/pricing.html", context)


def resources(request: HttpRequest) -> HttpResponse:
    # Fetch active categories with their active links pre-fetched in one query
    categories = (
        ResourceCategory.objects
        .filter(is_active=True)
        .prefetch_related("links")
    )

    # Build a JSON-serialisable structure for the existing modal JS
    resources_data = [
        {
            "id": str(cat.id),
            "emoji": cat.emoji,
            "title": cat.name,
            "tagline": cat.description,
            "links": [
                {
                    "title": link.title,
                    "url": link.href(),
                    "description": link.description,
                }
                for link in cat.links.filter(is_active=True)
            ],
        }
        for cat in categories
    ]

    context = {
        "active_page": "resources",
        "page_seo": PageSEO.objects.filter(page="resources").first(),
        "resources": resources_data,
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    "venus": "resource-narrative",
                    "earth": "resource-couples",
                    "mars": "resource-sex",
                    "jupiter": "resource-narrative",
                    "saturn": "resource-poly",
                    "uranus": "resource-poly",
                    "neptune": None,
                }
            )
        ),
    }
    return render(request, "pages/resources.html", context)


def trainings(request: HttpRequest) -> HttpResponse:
    published_trainings = Training.objects.filter(is_published=True)

    context = {
        "active_page": "trainings",
        "page_seo": PageSEO.objects.filter(page="trainings").first(),
        "site": SiteSettings.load(),
        "trainings": published_trainings,
        # Template uses this flag to decide between listing cards or placeholder
        "none_available": not published_trainings.exists(),
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    "venus": "trainings-main",
                    "earth": "trainings-main",
                    "mars": None,
                    "jupiter": "trainings-main",
                    "saturn": None,
                    "uranus": None,
                    "neptune": None,
                }
            )
        ),
    }
    return render(request, "pages/trainings.html", context)


def licensure(request: HttpRequest) -> HttpResponse:
    page = LicensurePage.load()
    context = {
        "active_page": "licensure",
        "page_seo": PageSEO.objects.filter(page="licensure").first(),
        "site": SiteSettings.load(),
        "page": page,
        "consult_booking_message": page.consult_booking_message,
        "renewal_booking_message": page.renewal_booking_message,
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    "venus": "licensure-intro",
                    "earth": "licensure-intro",
                    "mars": "licensure-rates",
                    "jupiter": None,
                    "saturn": None,
                    "uranus": None,
                    "neptune": None,
                }
            ),
            constellation_layout='diagonal'
        ),
    }
    return render(request, "pages/licensure.html", context)


def robots_txt(request: HttpRequest) -> HttpResponse:
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    site_url = settings.SITE_URL
    urls = [
        {"loc": f"{site_url}/",           "priority": "1.0", "changefreq": "weekly"},
        {"loc": f"{site_url}/pricing/",    "priority": "0.9", "changefreq": "monthly"},
        {"loc": f"{site_url}/resources/",  "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{site_url}/trainings/",  "priority": "0.6", "changefreq": "weekly"},
        {"loc": f"{site_url}/licensure/",  "priority": "0.7", "changefreq": "monthly"},
    ]
    return render(request, "sitemap.xml", {"urls": urls}, content_type="application/xml")
