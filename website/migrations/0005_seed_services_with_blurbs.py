from django.db import migrations

SERVICES = [
    {
        "label": "Individual Sex Therapy",
        "category": "Individual Sex Therapy",
        "blurb": (
            "Help with sex anxiety\n"
            "Difficulty enjoying sex\n"
            "Painful sex\n"
            "Sex with chronic illness or chronic pain\n"
            "Sex with HIV or herpes"
        ),
        "order": 1,
    },
    {
        "label": "Individual Relationship Therapy",
        "category": "Individual Relationship Therapy",
        "blurb": (
            "Difficulty making or maintaining relationships\n"
            "Inability to feel secure in relationships\n"
            "Trouble navigating the dating scene and forming meaningful connections\n"
            "Communication issues leading to loneliness or feeling misunderstood"
        ),
        "order": 2,
    },
    {
        "label": "LGBTQIA+ Affirming Therapy",
        "category": "LGBTQIA+ Affirming Therapy",
        "blurb": (
            "Identity exploration\n"
            "Sexuality exploration\n"
            "Sex and relationship therapy for queer individuals and couples\n"
            "Intersex-affirming individual and sex therapy"
        ),
        "order": 3,
    },
    {
        "label": "Polyamory & Ethical Non-Monogamy (ENM) Relationship Therapy",
        "category": "Polyamory & Ethical Non-Monogamy (ENM) Relationship Therapy",
        "blurb": (
            "Support for individuals who are in or considering ENM relationships\n"
            "Managing jealousy\n"
            "Deconstructing monogamous relationship norms\n"
            "Therapy for couples, triads, and polycules"
        ),
        "order": 4,
    },
    {
        "label": "Neurodivergent-Affirming Therapy",
        "category": "Neurodivergent-Affirming Therapy",
        "blurb": (
            "Helping clients unmask and live more authentically\n"
            "Improving communication skills to strengthen relationships\n"
            "Support for parents of neurodivergent children\n"
            "Couples or sex therapy to help partners navigate and better understand neurodivergent differences"
        ),
        "order": 5,
    },
    {
        "label": "Couples Therapy",
        "category": "Couples Therapy",
        "blurb": (
            "Difficulties communicating\n"
            "Getting caught in unproductive relationship patterns\n"
            "Navigating differences in healthy, collaborative ways\n"
            "Decrease the effects of negative or unproductive cycles"
        ),
        "order": 6,
    },
    {
        "label": "Couples Sex Therapy",
        "category": "Couples Sex Therapy",
        "blurb": (
            "Differences in sexual desire or sexual experience\n"
            "Sexless relationships\n"
            "Difficulty discussing sex\n"
            "Asexual-affirming couples therapy\n"
            "Navigating painful intercourse as a couple"
        ),
        "order": 7,
    },
]


def seed_services(apps, schema_editor):
    Service = apps.get_model("website", "Service")
    # Clear existing services and replace with the full set
    Service.objects.all().delete()
    for data in SERVICES:
        Service.objects.create(**data)


def unseed_services(apps, schema_editor):
    Service = apps.get_model("website", "Service")
    Service.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0004_add_service_category_blurb"),
    ]

    operations = [
        migrations.RunPython(seed_services, reverse_code=unseed_services),
    ]
