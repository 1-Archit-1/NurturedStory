from django.db import models


# ---------------------------------------------------------------------------
# Singleton helpers
# ---------------------------------------------------------------------------

class SingletonModel(models.Model):
    """Base class for models that should only ever have one row."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion of the singleton row

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------

class SiteSettings(SingletonModel):
    """
    Global site content — one row, always.

    Website locations:
      - practice_name  → site <title> tag, header brand, footer
      - tagline        → hero lede on home page ("Relational and Sex Counseling"),
                         footer subtitle
      - phone          → pricing page 'Reach Out Directly' card + footer
      - email          → pricing page 'Reach Out Directly' card + footer +
                         trainings 'Get in Touch' link
      - about_practice → home page 'About the Practice' card (purple card, left column)
      - sliding_scale_note → pricing page, shown beneath the session rate rows
      - footer_text    → copyright line in the site footer
    """

    practice_name = models.CharField(max_length=120, default="Nurtured Story")
    tagline = models.CharField(max_length=200, default="Relational and Sex Counseling")
    phone = models.CharField(max_length=30, default="470-599-5630")
    email = models.EmailField(default="shel@nurturedstory.com")
    about_practice = models.TextField(
        blank=True,
        help_text="The 'About the Practice' blurb shown on the home page.",
    )
    sliding_scale_note = models.CharField(
        max_length=300,
        blank=True,
        default="✦ Sliding scale available — reach out to discuss what works for you.",
    )
    footer_text = models.CharField(
        max_length=300,
        blank=True,
        default="Copyright 2026 Nurtured Story",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.practice_name


class TherapistProfile(SingletonModel):
    """
    Shel's bio card — one row, always.

    Website locations:
      - name        → 'About Shel Pohnan' card heading on the home page
      - credentials → subtitle line under the name ("APC · Certified Sex Therapist")
      - bio         → body text in the teal 'About' card on the home page
      - photo       → profile photo displayed in the left column on the home page
    """

    name = models.CharField(max_length=120, default="Shel Pohnan")
    credentials = models.CharField(
        max_length=200,
        blank=True,
        default="APC · Certified Sex Therapist",
        help_text="Shown under the therapist name, e.g. 'APC · Certified Sex Therapist'",
    )
    bio = models.TextField(
        blank=True,
        help_text="Full bio shown in the 'About' card on the home page.",
    )
    photo = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True,
        help_text="Profile photo displayed on the home page.",
    )

    class Meta:
        verbose_name = "Therapist Profile"
        verbose_name_plural = "Therapist Profile"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Ordered list models
# ---------------------------------------------------------------------------

class Service(models.Model):
    """
    A single bullet point in the Services section on the home page.

    Website location:
      - label → each <li> inside the 'Services' card at the bottom of the home page
                (e.g. 'Individual sex therapy', 'Couples therapy', etc.)

    Use `order` to control the sequence. Toggle `is_active` to hide an item
    without deleting it.
    """

    label = models.CharField(max_length=300)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.label


class SessionRate(models.Model):
    """
    A single rate row on the Pricing page.

    Website location:
      - session_type      → row heading, e.g. 'Individual Session'
      - duration_minutes  → subtext, e.g. '50 minutes · one-on-one'
      - price             → bold price displayed on the right, e.g. '$150'
      - note              → optional line beneath all rate rows (shared sliding scale note
                            is handled in SiteSettings; this note is per-rate)

    Shown inside the purple 'Session Rates' card on the pricing page.
    """

    session_type = models.CharField(
        max_length=120,
        help_text="e.g. 'Individual Session' or 'Couples Session'",
    )
    duration_minutes = models.PositiveSmallIntegerField(
        help_text="Length of the session in minutes.",
    )
    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        help_text="Rate in USD.",
    )
    note = models.CharField(
        max_length=300,
        blank=True,
        help_text="Optional note shown beneath this rate row.",
    )
    booking_message = models.TextField(
        blank=True,
        default="",
        help_text=(
            "Pre-filled message inserted into the contact form when a visitor "
            "clicks 'Book' on this rate row. Use it to confirm the session type "
            "they're enquiring about, e.g. "
            "'Hi, I'm interested in booking an Individual Session (50 min, $150). "
            "Please let me know your availability.'"
        ),
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Session Rate"
        verbose_name_plural = "Session Rates"

    def __str__(self):
        return f"{self.session_type} — ${self.price}"


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

class ResourceCategory(models.Model):
    """
    A category card on the Resources page.

    Website location:
      - name        → card heading and modal title (e.g. 'Narrative Resources')
      - emoji       → large emoji displayed on the card and at the top of the modal
      - description → intro paragraph shown at the top of the modal when the card
                      is clicked (e.g. 'Narrative therapy invites us to...')
      - order       → left-to-right / top-to-bottom card order in the grid

    Each category contains ResourceLinks shown as a list inside its modal.
    """

    name = models.CharField(max_length=120)
    emoji = models.CharField(max_length=10, blank=True)
    description = models.TextField(
        blank=True,
        help_text="Intro text shown at the top of the modal when a card is opened.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Resource Category"
        verbose_name_plural = "Resource Categories"

    def __str__(self):
        return self.name


class ResourceLink(models.Model):
    """
    A single link inside a ResourceCategory modal.

    Website location:
      - title       → link text shown in the modal list
      - url         → the href the link points to
      - description → short subtext shown beneath the link title in the modal
      - order       → top-to-bottom order within the modal link list

    Links only appear inside the modal that opens when a category card is clicked.
    """

    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.CASCADE,
        related_name="links",
    )
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.CharField(
        max_length=400,
        blank=True,
        help_text="Short description shown beneath the link.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Resource Link"
        verbose_name_plural = "Resource Links"

    def __str__(self):
        return f"{self.category.name} — {self.title}"


# ---------------------------------------------------------------------------
# Trainings
# ---------------------------------------------------------------------------

class Training(models.Model):
    """
    A training or workshop listing on the Trainings page.

    Website location:
      - title       → card heading on the trainings page
      - description → body text beneath the heading
      - date        → optional date displayed on the card
      - signup_url  → optional 'Sign Up' / 'More Info' button link on the card

    When zero trainings have `is_published=True`, the page automatically
    shows the 'None currently available' placeholder card instead.
    """

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField(
        blank=True,
        null=True,
        help_text="Optional display date for the training.",
    )
    signup_url = models.URLField(
        blank=True,
        help_text="Optional link for sign-ups or more info.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(
        default=False,
        help_text="Only published trainings appear on the site. "
                  "When none are published the page shows 'None currently available'.",
    )

    class Meta:
        ordering = ["order", "date"]
        verbose_name = "Training"
        verbose_name_plural = "Trainings"

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# Contact submissions
# ---------------------------------------------------------------------------

class ContactSubmission(models.Model):
    """
    Stores messages submitted via the contact form on the Pricing page.

    Website location:
      - The form lives in the purple 'Send a Message' card on the right side
        of the pricing page. Submissions are saved here and visible in the
        admin under Contact Submissions.

    - is_read → toggle in the admin list to mark a message as seen
    - No public-facing display; admin read-only.
    """

    name = models.CharField(max_length=120)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=40, blank=True)
    message = models.TextField(max_length=2000)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(
        default=False,
        help_text="Mark as read once you've seen this message.",
    )

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"

    def __str__(self):
        return f"{self.name} ({self.email}) — {self.submitted_at:%Y-%m-%d %H:%M}"
