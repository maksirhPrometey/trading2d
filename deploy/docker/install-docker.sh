#!/usr/bin/env bash
# Docker Engine + Compose plugin на Ubuntu 24.04 (DigitalOcean Droplet).
set -euo pipefail

if command -v docker &>/dev/null; then
  echo "==> Docker вже встановлено: $(docker --version)"
  docker compose version
  exit 0
fi

echo "==> Встановлення Docker через get.docker.com"
curl -fsSL https://get.docker.com | sh

systemctl enable --now docker
docker --version
docker compose version

echo "==> Firewall (якщо ufw активний)"
ufw allow OpenSSH 2>/dev/null || true
ufw allow 80/tcp 2>/dev/null || true
ufw allow 443/tcp 2>/dev/null || true

if [ "$(free -g | awk '/^Mem:/{print $2}')" -lt 2 ]; then
  if [ ! -f /swapfile ]; then
    echo "==> RAM < 2G — додаємо 2G swap"
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
  fi
fi
