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
