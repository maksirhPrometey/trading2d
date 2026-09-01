#!/usr/bin/env bash
# Деплой TRADING 2D на DigitalOcean Droplet (Docker Compose).
# bash deploy/docker/deploy.sh [--pull]
# HTTP = docker-compose.yml. HTTPS = + prod.yml, якщо є сертифікат.
set -euo pipefail

cd "$(dirname "$0")/../.."

CERT_PATH="/etc/letsencrypt/live/trading2d.com/fullchain.pem"
EXPECTED_SERVICES=(db web nginx)

if [ -f "$CERT_PATH" ]; then
  echo "==> SSL cert знайдено — HTTPS compose"
  COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
  HTTPS_MODE=1
else
  echo "==> SSL cert відсутній — HTTP-only (до certbot)"
  COMPOSE=(docker compose -f docker-compose.yml)
  HTTPS_MODE=0
fi

if [ "${1:-}" = "--pull" ]; then
  if [ -d .git ]; then
    echo "==> git pull origin main"
    git fetch origin
    git checkout main
    git pull --ff-only origin main
  else
    echo "FATAL: --pull потребує git-клону в /var/www/trading2d"
    exit 1
  fi
fi

echo "==> Звільняємо порти 80/443 від host nginx/httpd/gunicorn"
systemctl stop nginx 2>/dev/null || true
systemctl disable nginx 2>/dev/null || true
systemctl stop httpd 2>/dev/null || true
systemctl stop apache2 2>/dev/null || true
systemctl stop gunicorn 2>/dev/null || true
for svc in $(systemctl list-units --type=service --all 2>/dev/null | grep -o 'gunicorn-[^ ]*\.service' || true); do
  systemctl stop "$svc" 2>/dev/null || true
done

if [ "$HTTPS_MODE" -eq 0 ]; then
  docker compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true
fi

echo "==> Build web (обов'язково при зміні .py / requirements)"
"${COMPOSE[@]}" build web

echo "==> Up (перший up нефатальний — ERR-52)"
"${COMPOSE[@]}" up -d || echo "WARN: перший up повернув помилку — фінальний up нижче"

echo "==> Чекаємо web healthy..."
for _ in $(seq 1 60); do
  if "${COMPOSE[@]}" exec -T web \
    python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz/', timeout=2)" \
    >/dev/null 2>&1; then
    echo "==> web OK"
    break
  fi
  sleep 3
done

"${COMPOSE[@]}" up -d

echo "==> Інвентаризація сервісів"
"${COMPOSE[@]}" ps
missing=0
for svc in "${EXPECTED_SERVICES[@]}"; do
  cid="$("${COMPOSE[@]}" ps -q "$svc" 2>/dev/null || true)"
  if [ -z "$cid" ]; then
    echo "WARN: сервіс відсутній: $svc"
    missing=1
    continue
  fi
  state="$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null || echo missing)"
  if [ "$state" != "running" ]; then
    echo "WARN: сервіс не running ($state): $svc"
    missing=1
  fi
done
if [ "$missing" -ne 0 ]; then
  echo "FATAL: не всі сервіси running"
  "${COMPOSE[@]}" logs --tail=50
  exit 1
fi

echo "==> Django check"
"${COMPOSE[@]}" exec -T web python manage.py check

echo "==> Smoke"
curl -sf http://127.0.0.1/healthz/ && echo " HTTP healthz OK" || echo "WARN: HTTP healthz failed"
if [ "$HTTPS_MODE" -eq 1 ]; then
  curl -sfk https://127.0.0.1/healthz/ && echo " HTTPS healthz OK" || echo "WARN: HTTPS healthz failed"
else
  echo "INFO: HTTPS ще недоступний — DNS + certbot, потім знову deploy.sh"
fi

echo "==> Логи: ${COMPOSE[*]} logs -f web nginx"
