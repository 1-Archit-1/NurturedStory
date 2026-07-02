from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ContactForm

RESOURCES = [
    {
        "id": "narrative",
        "emoji": "📖",
        "title": "Narrative Resources",
        "tagline": "Rewriting the stories that shape us",
        "intro": (
            "Narrative therapy invites us to separate our identity from our problems, "
            "recognizing that we are not our struggles and we can re-author our story."
        ),
        "items": [
            {
                "heading": "Externalizing the Problem",
                "description": "See problems as separate from who you are, which opens room for agency.",
            },
            {
                "heading": "Re-authoring Conversations",
                "description": "Identify overlooked moments of resilience and build preferred narratives.",
            },
            {
                "heading": "Witnessing Practices",
                "description": "Use community and reflection to strengthen meaningful identity shifts.",
            },
            {
                "heading": "Recommended Reading",
                "description": "Narrative Means to Therapeutic Ends and Maps of Narrative Practice are strong starters.",
            },
        ],
    },
    {
        "id": "couples",
        "emoji": "💫",
        "title": "Relationship and Couples",
        "tagline": "Building connection and understanding together",
        "intro": (
            "Healthy relationships grow through communication, trust, and repair. "
            "Support can help partners move from conflict cycles to connection."
        ),
        "items": [
            {
                "heading": "Communication Tools",
                "description": "Learn practical ways to express needs and listen without escalating conflict.",
            },
            {
                "heading": "Attachment and Bonding",
                "description": "Understand attachment patterns and build safer emotional connection.",
            },
            {
                "heading": "Conflict as Connection",
                "description": "Reframe conflict as a pathway to understanding, repair, and closeness.",
            },
            {
                "heading": "Non-Monogamy Affirming",
                "description": "Affirming care for consensual relationship structures beyond convention.",
            },
        ],
    },
    {
        "id": "sex",
        "emoji": "🌹",
        "title": "Sex and Intimacy",
        "tagline": "Exploring pleasure, identity, and wholeness",
        "intro": (
            "Sex-positive, kink-aware counseling creates room to explore desire, boundaries, "
            "and identity without shame or pathologizing."
        ),
        "items": [
            {
                "heading": "Sex-Positive Framework",
                "description": "Approach sexuality with curiosity, consent, and affirmation.",
            },
            {
                "heading": "Pleasure and Desire",
                "description": "Reconnect with what feels good and identify barriers to intimacy.",
            },
            {
                "heading": "Sexual Health and Shame",
                "description": "Unpack inherited narratives and build an integrated sense of self.",
            },
            {
                "heading": "Kink-Aware Practice",
                "description": "Non-judgmental support centered on consent, communication, and safety.",
            },
        ],
    },
    {
        "id": "poly",
        "emoji": "♾️",
        "title": "Poly and Non-Monogamy",
        "tagline": "Navigating love beyond convention",
        "intro": (
            "Ethical non-monogamy includes many valid structures. "
            "Affirming support helps with clarity, agreements, and emotional skill building."
        ),
        "items": [
            {
                "heading": "Getting Started",
                "description": "Guidance for early conversations, agreements, and pacing.",
            },
            {
                "heading": "Jealousy and Compersion",
                "description": "Develop tools to regulate jealousy and cultivate security.",
            },
            {
                "heading": "Relationship Structures",
                "description": "Explore hierarchical, non-hierarchical, solo poly, and RA models.",
            },
            {
                "heading": "Community and Identity",
                "description": "Navigate visibility, belonging, and values-aligned support systems.",
            },
        ],
    },
]


SOLAR_SYSTEM = [
    {"id": "mercury", "label": "Mercury", "size": 34, "palette": "slate"},
    {"id": "venus", "label": "Venus", "size": 40, "palette": "rose"},
    {"id": "earth", "label": "Earth", "size": 45, "palette": "blue"},
    {"id": "mars", "label": "Mars", "size": 39, "palette": "champagne"},
    {"id": "jupiter", "label": "Jupiter", "size": 160, "palette": "midnight"},
    {"id": "saturn", "label": "Saturn", "size": 119, "palette": "sage", "ring": True},
    {"id": "uranus", "label": "Uranus", "size": 84, "palette": "dusk-teal"},
    {"id": "neptune", "label": "Neptune", "size": 69, "palette": "violet"},
    {"id": "pluto", "label": "Pluto", "size": 17, "palette": "slate"},
]


def build_scene(planets: list[dict]) -> dict:
    return {
        "stars": 120,
        "constellations": [
            {
                "id": "big_dipper",
                "label": "Big Dipper",
                "color": "rgba(180, 210, 255, 0.42)",
                "points": [
                    {"x": 14, "y": 16},
                    {"x": 18, "y": 21},
                    {"x": 15, "y": 27},
                    {"x": 11, "y": 23},
                    {"x": 8, "y": 17},
                    {"x": 6, "y": 12},
                    {"x": 4, "y": 7},
                ],
            },
            {
                "id": "orion",
                "label": "Orion",
                "color": "rgba(168, 210, 255, 0.36)",
                "points": [
                    {"x": 74, "y": 21},
                    {"x": 80, "y": 22},
                    {"x": 75, "y": 28},
                    {"x": 77, "y": 28},
                    {"x": 79, "y": 28},
                    {"x": 75, "y": 34},
                    {"x": 81, "y": 34},
                    {"x": 78, "y": 16},
                ],
            },
            {
                "id": "gemini",
                "label": "Gemini",
                "color": "rgba(180, 210, 255, 0.32)",
                "points": [
                    {"x": 55, "y": 8},
                    {"x": 59, "y": 13},
                    {"x": 55, "y": 18},
                    {"x": 59, "y": 19},
                    {"x": 54, "y": 23},
                    {"x": 58, "y": 24},
                    {"x": 59, "y": 27},
                    {"x": 56, "y": 4},
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


def home(request: HttpRequest) -> HttpResponse:
    context = {
        "active_page": "home",
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    #"mercury": "home-title",
                    "venus": "profile-photo",
                    "earth": "profile-photo",
                    "mars": "about-practice",
                    "jupiter": "about-practice",
                    "saturn": "about-me",
                    "uranus": "about-me",
                    "neptune": None,
                }
            )
        ),
    }
    return render(request, "pages/home.html", context)


def pricing(request: HttpRequest) -> HttpResponse:
    submitted = request.GET.get("submitted") == "1"

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # This is a template starter. Add email/database handling here later.
            return redirect(f"{reverse('pricing')}?submitted=1")
    else:
        form = ContactForm()

    context = {
        "active_page": "pricing",
        "form": form,
        "submitted": submitted,
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    #"mercury": "pricing-title",
                    "venus": "session-rates",
                    "earth": "session-rates",
                    "mars": "direct-contact",
                    "jupiter": "session-rates",
                    "saturn": "contact-form",
                    "uranus": "contact-form",
                    "neptune": None,
                }
            )
        ),
    }
    return render(request, "pages/pricing.html", context)


def resources(request: HttpRequest) -> HttpResponse:
    context = {
        "active_page": "resources",
        "resources": RESOURCES,
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    #"mercury": "resources-title",
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
    context = {
        "active_page": "trainings",
        "cosmic_scene": build_scene(
            solar_planets(
                {
                    #"mercury": "trainings-title",
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
