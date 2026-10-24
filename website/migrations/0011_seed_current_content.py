import json
from pathlib import Path

from django.db import migrations

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "current_content.json"


def load_fixture(apps, schema_editor):
    """
    Load the current live content snapshot into the DB.

    Uses the *historical* models (apps.get_model) rather than call_command("loaddata").
    loaddata goes through today's models, so on a fresh database it tries to write
    columns that later migrations add (e.g. SiteSettings.contact_recipient_email from
    0014) and the whole migrate run fails. Fields the historical model doesn't know
    are skipped. Like loaddata, each record is upserted by primary key.

    Databases that already applied 0011 never run this again, so this only affects
    fresh databases (new environments, staging, the test runner).
    """
    records = json.loads(FIXTURE.read_text(encoding="utf-8"))

    for record in records:
        app_label, model_name = record["model"].split(".")
        Model = apps.get_model(app_label, model_name)
        fields = {f.name: f for f in Model._meta.concrete_fields}

        values = {}
        for name, value in record["fields"].items():
            field = fields.get(name)
            if field is None:
                continue  # field added after this migration
            # Fixtures store foreign keys as the related primary key
            values[field.attname] = value

        Model.objects.update_or_create(pk=record["pk"], defaults=values)


def noop_reverse(apps, schema_editor):
    """
    Reverse migration is a no-op — we don't want to blow away site content
    just because someone rolled back one migration. If a rollback is needed,
    handle it manually via the admin or a separate migration.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0010_add_home_card_headings"),
    ]

    operations = [
        migrations.RunPython(load_fixture, noop_reverse),
    ]
