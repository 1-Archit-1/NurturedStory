from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ContactForm
from .models import (
    ContactSubmission,
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
                "id": "big_dipper",
                "label": "Big Dipper",
                "color": "rgba(180, 210, 255, 0.42)",
                "points": [
                    {"x": 5,  "y": 20},
                    {"x": 25, "y": 35},
                    {"x": 50, "y": 45},
                    {"x": 40, "y": 65},
                    {"x": 75, "y": 80},
                    {"x": 95, "y": 50},
                    {"x": 80, "y": 25},
                ],
            },
            {
                "id": "orion",
                "label": "Orion",
                "color": "rgba(168, 210, 255, 0.36)",
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
                "id": "gemini",
                "label": "Gemini",
                "color": "rgba(180, 210, 255, 0.32)",
                "points": [
                    {"x": 20, "y": 10},
                    {"x": 50, "y": 25},
                    {"x": 10, "y": 60},
                    {"x": 40, "y": 65},
                    {"x": 5,  "y": 95},
                    {"x": 30, "y": 100},
                    {"x": 60, "y": 80},
                    {"x": 40, "y": 5},
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
        # Singleton — always one row; .load() creates it if missing
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
            constellation_layout= 'diagonal'
        ),
    }
    return render(request, "pages/home.html", context)


def pricing(request: HttpRequest) -> HttpResponse:
    submitted = request.GET.get("submitted") == "1"

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save submission to the DB so Shel can read it in the admin
            ContactSubmission.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data.get("phone", ""),
                message=form.cleaned_data["message"],
            )
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
        "form": form,
        "submitted": submitted,
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
                    "url": link.url,
                    "description": link.description,
                }
                for link in cat.links.filter(is_active=True)
            ],
        }
        for cat in categories
    ]

    context = {
        "active_page": "resources",
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
        # site.email used for the 'Get in Touch' mailto link
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
