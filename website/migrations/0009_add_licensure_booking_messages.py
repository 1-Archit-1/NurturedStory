from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0008_seed_sex_intimacy_resources"),
    ]

    operations = [
        migrations.AddField(
            model_name="licensurepage",
            name="consult_booking_message",
            field=models.TextField(
                blank=True,
                default=(
                    "Hi, I'm interested in booking a Licensure Consultation ($50 / hour). "
                    "Please let me know your availability."
                ),
                help_text=(
                    "Pre-filled message inserted into the contact form when a visitor "
                    "clicks 'Book a Consultation' on the Licensure Consultation card."
                ),
            ),
        ),
        migrations.AddField(
            model_name="licensurepage",
            name="renewal_booking_message",
            field=models.TextField(
                blank=True,
                default=(
                    "Hi, I'm interested in booking a CE Renewal Consultation ($75). "
                    "Please let me know your availability."
                ),
                help_text=(
                    "Pre-filled message inserted into the contact form when a visitor "
                    "clicks 'Book a Consultation' on the CE Renewal card."
                ),
            ),
        ),
    ]
