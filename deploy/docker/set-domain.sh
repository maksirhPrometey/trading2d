#!/usr/bin/env bash
# Підставляє домен у deploy/nginx/docker.prod.conf.
# Використання: bash deploy/docker/set-domain.sh trading2d.com
set -euo pipefail

cd "$(dirname "$0")/../.."

DOMAIN="${1:-}"
if [ -z "$DOMAIN" ]; then
  echo "Usage: bash deploy/docker/set-domain.sh yourdomain.com"
  exit 1
fi

CONF="deploy/nginx/docker.prod.conf"
if [ ! -f "$CONF" ]; then
  echo "ERROR: $CONF not found"
  exit 1
fi

CURRENT="$(sed -n 's|.* /etc/letsencrypt/live/\([^/]*\)/fullchain.pem.*|\1|p' "$CONF" | head -1)"
if [ -z "$CURRENT" ]; then
  echo "ERROR: cannot detect current domain in $CONF"
  exit 1
fi

if [ "$CURRENT" != "$DOMAIN" ]; then
  sed -i.bak "s/${CURRENT}/${DOMAIN}/g" "$CONF"
  rm -f "${CONF}.bak"
fi

echo "==> Updated $CONF → domain=${DOMAIN}"
grep -E "server_name|ssl_certificate" "$CONF" | head -6
