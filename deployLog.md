# Deployment Guide — Nurtured Story

## Architecture Overview

```
Browser → Cloudflare (CDN + HTTPS) → OCI VPS → Coolify (Traefik proxy) → Docker container (Gunicorn + Django)
```

- **Coolify** manages deployments, container lifecycle, and HTTPS certificates
- **Cloudflare** sits in front for CDN, DDoS protection, and DNS
- **Django + Gunicorn** serves the app (2 workers, 2 threads each)
- **WhiteNoise** serves static files (CSS/JS) baked into the image
- **Django `serve()`** serves uploaded media files at runtime
- **SQLite** is the database, stored on a persistent Docker volume
- **Docker volumes** persist the database and uploaded media across redeployments

---

## Prerequisites

- OCI (or any VPS) with Ubuntu, SSH access
- Docker + Docker Compose installed
- Coolify installed and running on the VPS
- Cloudflare account with the domain's DNS pointing to the VPS IP
- Git repository access (Coolify pulls from git)

---

## First-Time Setup

### 1. VPS preparation

Make swap space (prevents OOM kills on small instances):
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Install Docker:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 2. Install Coolify

Follow the official one-liner at https://coolify.io/docs/installation.
Coolify runs on port 3000 by default — change it if it conflicts with another service.

### 3. Add the project in Coolify

- New Resource → Docker Compose
- Point at the git repository
- Set the compose file to `docker-compose.yml` (base file only — not the Caddy variant)
- Coolify's built-in Traefik proxy handles HTTPS automatically

### 4. Set environment variables in Coolify

Go to the service → Environment Variables. Add all values from `.env.example`:

| Variable | Description |
|---|---|
| `DJANGO_ENV` | Set to `production` |
| `SECRET_KEY` | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `PRODUCTION_ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `SITE_URL` | `https://yourdomain.com` |
| `EMAIL_HOST_USER` | Gmail address for sending contact form notifications |
| `EMAIL_HOST_PASSWORD` | Gmail App Password (16 chars, from myaccount.google.com/apppasswords) |
| `CONTACT_RECIPIENT_EMAIL` | Email that receives contact form submissions |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 API access key |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 API secret |
| `R2_ENDPOINT_URL` | `https://<account_id>.r2.cloudflarestorage.com` |
| `R2_BUCKET` | R2 bucket name (e.g. `nurturedstory-backups`) |

### 5. Configure Coolify domain

- In the service settings, set the domain to `yourdomain.com`
- Coolify auto-provisions a Let's Encrypt certificate

### 6. Deploy

Click Deploy in Coolify, or push to the connected git branch.

On first deploy, Coolify will:
1. Build the Docker image (installs deps, runs `collectstatic`)
2. Start the container
3. `entrypoint.sh` runs `migrate` then starts Gunicorn

### 7. Create the Django superuser

After the first deploy, run once:
```bash
docker exec <container-name> python manage.py createsuperuser
```

Find the container name with `docker ps`.

### 8. Configure Cloudflare

- DNS: A record pointing `yourdomain.com` → VPS IP (proxied = orange cloud ON)
- SSL/TLS mode: **Full** (or Full strict if Coolify cert is valid)
- Always Use HTTPS: ON (under SSL/TLS → Edge Certificates)

---

## Set Up Automated Backups

The app backs up SQLite to Cloudflare R2 on a schedule (daily/weekly/monthly).
R2 credentials must be set as env vars (see step 4 above).

In Coolify → Service → Scheduled Tasks, create three tasks:

| Name | Command | Schedule | Retention |
|---|---|---|---|
| Daily backup | `python scripts/backup.py daily` | `0 3 * * *` | 3 days |
| Weekly backup | `python scripts/backup.py weekly` | `0 4 * * 0` | 4 weeks |
| Monthly backup | `python scripts/backup.py monthly` | `0 5 1 * *` | 2 months |
| Media sync | `python scripts/backup.py media` | `0 2 * * 0` | Latest state (no versioning) |

Test manually after setup:
```bash
docker exec <container-name> python /app/scripts/backup.py daily
```

---

## Set Up Health Check Alerts

In Coolify → Settings → Notifications:
- Add SMTP credentials (use the same Gmail + App Password)
- Enable "Container status changed" notifications

The container exposes `/healthz` — it checks Django is running and the database is reachable.
Docker polls it every 30s. After 3 failures, the container is marked unhealthy and auto-restarts.
Coolify sends an email when the container state changes.

---

## Routine Deployments (after setup)

Push to the connected git branch → Coolify auto-deploys.

The deployment process:
1. Builds a new image (installs deps, runs `collectstatic`)
2. Stops the old container
3. Starts the new container
4. `entrypoint.sh` runs `migrate` (safe to run on every deploy)
5. Gunicorn starts serving requests

**Data is safe during deploys** — the `sqlite_data` and `media_data` Docker volumes are not touched by redeployments.

---

## Restoring from Backup

**Normal redeployments do not require a restore** — the `sqlite_data` and `media_data` Docker volumes survive redeployments automatically. This section covers disaster recovery only: VPS migration, accidental volume deletion, or a fresh server setup.

### What needs restoring

| Data | Stored in | Backed up to |
|---|---|---|
| Database (all content, contacts, settings) | `sqlite_data` Docker volume | R2 — `daily/`, `weekly/`, `monthly/` prefixes |
| Uploaded files (PDFs, therapist photo) | `media_data` Docker volume | R2 — `media/` prefix (weekly sync) |

### Step 1 — List available backups in R2

```bash
# Install AWS CLI temporarily (or use the R2 dashboard)
pip install awscli

# Configure credentials
export AWS_ACCESS_KEY_ID=<your-r2-access-key>
export AWS_SECRET_ACCESS_KEY=<your-r2-secret-key>

# List available backups
aws --endpoint-url <R2_ENDPOINT_URL> s3 ls s3://<R2_BUCKET>/daily/
aws --endpoint-url <R2_ENDPOINT_URL> s3 ls s3://<R2_BUCKET>/weekly/
aws --endpoint-url <R2_ENDPOINT_URL> s3 ls s3://<R2_BUCKET>/monthly/
```

Pick the most recent backup file you want to restore from.

### Step 2 — Download the backup

```bash
aws --endpoint-url <R2_ENDPOINT_URL> s3 cp \
  s3://<R2_BUCKET>/daily/db-20260101-030000.sqlite3 \
  ~/db-restore.sqlite3
```

### Step 3 — Deploy the app first

Make sure the container is running and the `sqlite_data` volume exists before restoring. If setting up a fresh server, complete the full first-time setup (steps 1–6) first, then restore.

On a fresh server the first start migrates an empty database and seeds it with the default content snapshot (`website/fixtures/current_content.json`), so the site comes up with placeholder content. The restore below replaces that whole database with your backup. Afterwards, `migrate` only applies migrations newer than the backup.

### Step 4 — Stop the container

```bash
docker stop <container-name>
```

This prevents writes to the database during the restore. Note: `docker stop` only pauses the container — `docker cp` works on both running and stopped containers.

### Step 5 — Copy the backup into the volume

```bash
# Works whether the container is running or stopped
docker cp ~/db-restore.sqlite3 <container-name>:/app/data/db.sqlite3
```

If the container has been fully removed (not just stopped), use a temporary container with the volume mounted:
```bash
docker run --rm \
  -v sqlite_data:/app/data \
  -v ~/db-restore.sqlite3:/tmp/restore.sqlite3 \
  python:3.12-slim \
  cp /tmp/restore.sqlite3 /app/data/db.sqlite3
```

### Step 6 — Restart the container

```bash
docker start <container-name>
```

Or trigger a redeploy from Coolify. The `entrypoint.sh` will run `migrate` on startup — safe to run against a restored database.

### Step 7 — Verify

- Visit the site and confirm content is intact
- Log in to the Django admin and check contact submissions, resource links, site settings
- Run a health check: `curl https://yourdomain.com/healthz`

### Restoring uploaded media files

Media files are synced to R2 weekly under the `media/` prefix.

**Restore from R2:**
```bash
# Download all media files from R2 to a local directory
aws --endpoint-url <R2_ENDPOINT_URL> s3 sync \
  s3://<R2_BUCKET>/media/ \
  ~/media-restore/

# Copy them into the running container
docker cp ~/media-restore/. <container-name>:/app/media/
```

Or using a temporary container if the web container is stopped:
```bash
docker run --rm \
  -v media_data:/app/media \
  -v ~/media-restore:/tmp/restore \
  python:3.12-slim \
  sh -c "cp -r /tmp/restore/. /app/media/"
```

---

## Self-Hosted Deploy (VPS without Coolify)

Uses Caddy as the reverse proxy instead of Traefik.

```bash
cp .env.example .env
# Fill in .env values, then:
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d --build
```

Run post-deploy commands:
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## Useful Commands

```bash
# View live logs
docker logs <container-name> -f

# Open a shell inside the container
docker exec -it <container-name> sh

# Run a Django management command
docker exec <container-name> python manage.py <command>

# Check container health
docker inspect <container-name> | grep -A5 Health

# Manually back up the database
docker exec <container-name> python /app/scripts/backup.py daily

# Copy the database out of the container (emergency backup)
docker cp <container-name>:/app/data/db.sqlite3 ~/db-emergency-backup.sqlite3

# Copy media files out (emergency backup)
docker cp <container-name>:/app/media ~/media-emergency-backup
```

---

## Troubleshooting

**Site is down / 502 Bad Gateway**
```bash
docker ps                      # is the container running?
docker logs <container-name>   # check for errors
```

**Contact form not sending emails**
- Check `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set in Coolify
- Confirm the Gmail App Password is correct (16 chars, no spaces)
- Check logs: `docker logs <container-name> | grep email`

**Uploaded files returning 404**
- Confirm `media_data` volume is mounted: `docker exec <container-name> ls /app/media`
- If empty, the file was uploaded before the volume was added — re-upload via admin

**Static files not loading (after deploy)**
- WhiteNoise serves from `staticfiles/` which is built into the image
- If CSS is missing, the build may have failed — check Coolify build logs

**Database issues**
- Check the volume is mounted: `docker exec <container-name> ls /app/data`
- Run migrations manually: `docker exec <container-name> python manage.py migrate`
