#!/usr/bin/env bash
# Щоденний бекап PostgreSQL + media.
# cron: 0 3 * * * /var/www/trading2d/deploy/docker/backup.sh >> /var/log/trading2d-backup.log 2>&1
set -euo pipefail

cd "$(dirname "$0")/../.."

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

BACKUP_DIR="${BACKUP_DIR:-/var/backups/trading2d}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
DUMP_FILE="${BACKUP_DIR}/db_${TIMESTAMP}.sql.gz"
MEDIA_FILE="${BACKUP_DIR}/media_${TIMESTAMP}.tar.gz"

COMPOSE=(docker compose -f docker-compose.yml)
if [ -f /etc/letsencrypt/live/trading2d.com/fullchain.pem ]; then
  COMPOSE=(docker compose -f docker-compose.yml -f docker-compose.prod.yml)
fi

mkdir -p "$BACKUP_DIR"

echo "==> [$(date -Iseconds)] Backup start"

"${COMPOSE[@]}" exec -T db \
  pg_dump -U "${POSTGRES_USER:-trading2d}" "${POSTGRES_DB:-trading2d}" | gzip > "$DUMP_FILE"

if [ ! -s "$DUMP_FILE" ]; then
  echo "FATAL: дамп порожній: ${DUMP_FILE}" >&2
  rm -f "$DUMP_FILE"
  exit 1
fi
echo "==> DB: $(du -h "$DUMP_FILE" | cut -f1)"

media_cid="$("${COMPOSE[@]}" ps -q web 2>/dev/null || true)"
if [ -n "$media_cid" ]; then
  docker run --rm --volumes-from "$media_cid" -v "$BACKUP_DIR":/backup alpine \
    tar czf "/backup/media_${TIMESTAMP}.tar.gz" -C /app media
  echo "==> media: $(du -h "$MEDIA_FILE" | cut -f1)"
fi

echo "==> Ротація старші за ${RETENTION_DAYS} днів"
find "$BACKUP_DIR" -name 'db_*.sql.gz' -mtime "+${RETENTION_DAYS}" -print -delete
find "$BACKUP_DIR" -name 'media_*.tar.gz' -mtime "+${RETENTION_DAYS}" -print -delete

echo "==> [$(date -Iseconds)] Backup done"
