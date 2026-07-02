# Django Version of Therapy Website Prototype

This folder contains a clean Django rewrite of the basic prototype structure.

## What Was Carried Over

- Core page structure: Home, Pricing and Appointments, Resources, Trainings
- Contact form on the pricing page
- Shared site header and footer
- Reusable styling with a single static CSS file

## Project Layout

```text
django_site/
  config/                  # Django project config
  website/                 # App with views, routes, forms
  templates/
    pages/                 # Page templates
    partials/              # Shared template pieces
  static/css/              # Site styles
  manage.py
  requirements.txt
```

## Run Locally

1. Create and activate a virtual environment:
   - Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Apply initial migrations:
   - `python manage.py migrate`
4. Start the server:
   - `python manage.py runserver`
5. Open `http://127.0.0.1:8000`

## Notes

- The contact form currently validates input and redirects with a success state.
- You can plug in email sending or database persistence in `website/views.py`.
- Styling is intentionally simple and centralized for easy editing.
