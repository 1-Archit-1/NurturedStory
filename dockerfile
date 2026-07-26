# Start with a lightweight Python image
FROM python:3.12-slim 

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# We only need Gunicorn now
RUN pip install gunicorn

COPY . /app/

# Collect static files into /app/staticfiles at build time
# Dummy SECRET_KEY is fine here — collectstatic doesn't need a real one
RUN DJANGO_ENV=production SECRET_KEY=build-placeholder python manage.py collectstatic --noinput

RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
