from django.db import migrations


def seed_seo(apps, schema_editor):
    PageSEO = apps.get_model("website", "PageSEO")
    LocalBusinessSEO = apps.get_model("website", "LocalBusinessSEO")

    # Per-page SEO defaults — match the hardcoded descriptions we had in templates
    pages = [
        {
            "page": "home",
            "meta_title": "Nurtured Story | Relational & Sex Therapy — Atlanta Area, GA",
            "meta_description": (
                "Relational therapy and sex counseling through Nurtured Story — "
                "in person in the Atlanta area (Decatur, GA) and virtual therapy "
                "across Georgia. Narrative-based, affirming approach."
            ),
        },
        {
            "page": "pricing",
            "meta_title": "Pricing & Appointments | Nurtured Story",
            "meta_description": (
                "Session rates and appointment booking for relational therapy and sex "
                "counseling through Nurtured Story — in-person in the Atlanta area "
                "(Decatur, GA) and virtual sessions across Georgia. Sliding scale available."
            ),
        },
        {
            "page": "resources",
            "meta_title": "Resources | Nurtured Story",
            "meta_description": (
                "Curated therapy resources on narrative therapy, sex and intimacy, "
                "polyamory, and relational wellness from Nurtured Story."
            ),
        },
        {
            "page": "trainings",
            "meta_title": "Trainings | Nurtured Story",
            "meta_description": (
                "Trainings and workshops on narrative therapy, relational wellness, "
                "and affirmative clinical practice by Shel Pohnan, APC."
            ),
        },
        {
            "page": "licensure",
            "meta_title": "Georgia LPC/APC Licensure Consultation | Nurtured Story",
            "meta_description": (
                "Georgia LPC/APC licensure consultation for counselors-in-training "
                "and associate-level clinicians. Application guidance, supervision "
                "requirements, and CE renewal support."
            ),
        },
    ]

    for data in pages:
        PageSEO.objects.update_or_create(page=data["page"], defaults={
            "meta_title": data["meta_title"],
            "meta_description": data["meta_description"],
        })

    # Local business structured data defaults
    LocalBusinessSEO.objects.update_or_create(pk=1, defaults={
        "city": "Decatur",
        "state": "GA",
    })


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0012_add_page_seo_models"),
    ]

    operations = [
        migrations.RunPython(seed_seo, migrations.RunPython.noop),
    ]
