from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    """
    Load the current live content snapshot into the DB.
    Uses call_command('loaddata') so it works consistently across environments.
    """
    call_command("loaddata", "current_content.json", app_label="website")


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
