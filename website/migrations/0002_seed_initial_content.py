from django.db import migrations


def seed_forward(apps, schema_editor):
    SiteSettings = apps.get_model("website", "SiteSettings")
    TherapistProfile = apps.get_model("website", "TherapistProfile")
    Service = apps.get_model("website", "Service")
    SessionRate = apps.get_model("website", "SessionRate")
    ResourceCategory = apps.get_model("website", "ResourceCategory")
    ResourceLink = apps.get_model("website", "ResourceLink")
    Training = apps.get_model("website", "Training")

    # -----------------------------------------------------------------------
    # Site Settings
    # -----------------------------------------------------------------------
    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={
            "practice_name": "Nurtured Story",
            "tagline": "Relational and Sex Counseling",
            "phone": "470-599-5630",
            "email": "shel@nurturedstory.com",
            "about_practice": (
                "At Nurtured Story we utilize narrative therapy to explore, understand and reauthor "
                "the difficult stories influencing your relationships and sex life.\n"
                "The dominant narrative of our lives is influenced by the stories that shine the "
                "brightest in the constellation of our lives. We will work together to identify "
                "multiple stars in the solar systems of you to create new, better fitting constellations.\n"
                "To do this we will utilize a mix of exploratory conversation, metaphor, art therapy "
                "(if you are into that), humor, and skill building.\n"
                "At Nurtured Story we specialize in supporting people with underrepresented stories; "
                "queer, neurodivergent, polyamorous or anyone a grandpa might define as \"a little "
                "different.\" We don't believe you need to \"fit in\" but we want to support you in "
                "finding the place you fit.\n"
                "We offer both in person and virtual service to remain accessible and inclusive to all "
                "Georgia residents, with our in person space located in Decatur, GA."
            ),
            "sliding_scale_note": "✦ Sliding scale available — reach out to discuss what works for you.",
            "footer_text": "Copyright 2026 Nurtured Story",
        },
    )

    # -----------------------------------------------------------------------
    # Therapist Profile
    # -----------------------------------------------------------------------
    TherapistProfile.objects.update_or_create(
        pk=1,
        defaults={
            "name": "Shel Pohnan",
            "credentials": "APC · Certified Sex Therapist",
            "bio": (
                "Neurodivergent counselor with a special interest in sexuality and relationships. "
                "I once spent a summer studying human sexuality at the University of Amsterdam. "
                "That training continues to shape the way I approach conversations about desire, "
                "identity and connection.\n"
                "I believe therapy works best when people are genuinely at ease. In my office we "
                "are curled up or criss cross on the couch, fidget buffet within arms reach, and "
                "shoes optional. Get comfortable to sit in discomfort. Discover a space where nothing "
                "is too awkward or \"too much\" to talk about. I'll do my best to foster a healing "
                "space to confront the effects of the problems keeping you stuck.\n"
                "My clients would describe me as warm, grounded, and comforting while also providing "
                "structure and challenging the problems without shaming or blaming the individual. "
                "It's like if stardew valley met the Oregon Trail, don't worry though we have "
                "treatment or dysentery."
            ),
        },
    )

    # -----------------------------------------------------------------------
    # Services
    # -----------------------------------------------------------------------
    services = [
        "Individual sex therapy",
        "Individual therapy to support and improve relationship skills (both romantic and platonic)",
        "LGBTQ and intersex affirming therapy",
        "Couples therapy",
        "Poly/ENM relationship therapy",
        "Couples/relationship sex therapy",
        "Neurodivergent affirming therapy for individuals, parents of neurodivergent children, and partners of neurodivergent people",
    ]
    for i, label in enumerate(services):
        Service.objects.get_or_create(label=label, defaults={"order": i, "is_active": True})

    # -----------------------------------------------------------------------
    # Session Rates
    # -----------------------------------------------------------------------
    SessionRate.objects.update_or_create(
        session_type="Individual Session",
        defaults={"duration_minutes": 50, "price": "150.00", "order": 0, "is_active": True},
    )
    SessionRate.objects.update_or_create(
        session_type="Couples Session",
        defaults={"duration_minutes": 80, "price": "200.00", "order": 1, "is_active": True},
    )

    # -----------------------------------------------------------------------
    # Resource Categories (cards) — links are placeholders to be filled later
    # -----------------------------------------------------------------------
    resource_data = [
        {
            "name": "Narrative Resources",
            "emoji": "📖",
            "description": (
                "Narrative therapy invites us to separate our identity from our problems, "
                "recognizing that we are not our struggles and we can re-author our story."
            ),
            "order": 0,
        },
        {
            "name": "Relationship and Couples",
            "emoji": "💫",
            "description": (
                "Healthy relationships grow through communication, trust, and repair. "
                "Support can help partners move from conflict cycles to connection."
            ),
            "order": 1,
        },
        {
            "name": "Sex and Intimacy",
            "emoji": "🌹",
            "description": (
                "Sex-positive, kink-aware counseling creates room to explore desire, boundaries, "
                "and identity without shame or pathologizing."
            ),
            "order": 2,
        },
        {
            "name": "Poly and Non-Monogamy",
            "emoji": "♾️",
            "description": (
                "Ethical non-monogamy includes many valid structures. "
                "Affirming support helps with clarity, agreements, and emotional skill building."
            ),
            "order": 3,
        },
    ]
    for data in resource_data:
        ResourceCategory.objects.update_or_create(
            name=data["name"],
            defaults={
                "emoji": data["emoji"],
                "description": data["description"],
                "order": data["order"],
                "is_active": True,
            },
        )

    # No Training rows — the page correctly shows 'None currently available'


def seed_reverse(apps, schema_editor):
    # Rolling back clears all seeded data
    for model_name in [
        "SiteSettings", "TherapistProfile", "Service",
        "SessionRate", "ResourceCategory", "ResourceLink", "Training",
    ]:
        apps.get_model("website", model_name).objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_forward, seed_reverse),
    ]
