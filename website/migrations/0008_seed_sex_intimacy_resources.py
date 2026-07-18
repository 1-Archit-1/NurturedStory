from django.db import migrations

SEX_INTIMACY_LINKS = [
    {
        "title": "Sensate Focus Touch",
        "url": "",
        "description": "Reconnect and quiet sex anxiety",
        "order": 1,
    },
    {
        "title": "Emily Nagoski's Worksheets (Come As You Are)",
        "url": "https://www.emilynagoski.com/come-as-you-are-worksheets",
        "description": "",
        "order": 2,
    },
    {
        "title": "A Woman's Touch Sexuality Resource Center",
        "url": "https://sexualityresources.com/",
        "description": "",
        "order": 3,
    },
    {
        "title": "Outercourse",
        "url": "",
        "description": "Fun without penetration!",
        "order": 4,
    },
]

SEX_INTIMACY_BLURB = (
    "Sexual health is relevant throughout a person\u2019s life. It is determined by the "
    "quality and safety of people\u2019s relationships: with oneself and other individuals, "
    "family, friends, and the society in which we live. Great sex starts with great safety."
)


def seed(apps, schema_editor):
    ResourceCategory = apps.get_model("website", "ResourceCategory")
    ResourceLink = apps.get_model("website", "ResourceLink")

    # Find the sex & intimacy category by name (case-insensitive partial match)
    cat = (
        ResourceCategory.objects
        .filter(name__icontains="sex")
        .first()
    )
    if cat is None:
        return  # Category doesn't exist yet — skip silently

    # Update the description/blurb
    cat.description = SEX_INTIMACY_BLURB
    cat.save()

    # Add links (skip if a link with that title already exists)
    for data in SEX_INTIMACY_LINKS:
        if not ResourceLink.objects.filter(category=cat, title=data["title"]).exists():
            ResourceLink.objects.create(category=cat, **data)


def unseed(apps, schema_editor):
    ResourceCategory = apps.get_model("website", "ResourceCategory")
    ResourceLink = apps.get_model("website", "ResourceLink")

    cat = ResourceCategory.objects.filter(name__icontains="sex").first()
    if cat is None:
        return
    for data in SEX_INTIMACY_LINKS:
        ResourceLink.objects.filter(category=cat, title=data["title"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0007_add_licensure_page_fix_credentials"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_code=unseed),
    ]
