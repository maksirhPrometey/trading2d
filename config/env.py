"""Мінімальний завантажувач .env без зовнішніх залежностей.

Читає файл `.env` у корені проєкту (якщо існує) і кладе значення
у os.environ, не перезаписуючи вже встановлені змінні середовища
(env середовища деплою завжди мають пріоритет над файлом).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(path=None):
    env_path = Path(path) if path else BASE_DIR / '.env'
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env(key, default=None):
    return os.environ.get(key, default)


def env_bool(key, default=False):
    value = os.environ.get(key)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(key, default=None, separator=','):
    value = os.environ.get(key)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


load_env_file()
