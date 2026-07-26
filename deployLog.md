## Coolify deploy
Point Coolify at the repo using docker-compose.yml (base file only).
Coolify's built-in Traefik proxy handles HTTPS automatically.

## Self-hosted deploy (VPS without Coolify)
Uses Caddy as the reverse proxy + static file server.

### make swap
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

### install docker and docker compose
cp .env.example .env
# fill in .env values, then:
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d --build

### python commands
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput










