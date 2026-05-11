#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate

# Render Free rejasida shell yo'qligi sababli superuserni deploy vaqtida yaratish.
if [ "${CREATE_SUPERUSER_ON_DEPLOY:-false}" = "true" ]; then
  python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()

if not username or not password:
    raise SystemExit(
        "Superuser yaratish o'tkazib yuborildi: "
        "DJANGO_SUPERUSER_USERNAME yoki DJANGO_SUPERUSER_PASSWORD to'ldirilmagan."
    )

User = get_user_model()
user, created = User.objects.get_or_create(
    username=username,
    defaults={
        "email": email,
        "is_staff": True,
        "is_superuser": True,
    },
)

changed = False
if not user.is_staff:
    user.is_staff = True
    changed = True
if not user.is_superuser:
    user.is_superuser = True
    changed = True
if email and user.email != email:
    user.email = email
    changed = True

# Har deployda shu env parol bilan yangilanadi (xavfsizlik uchun keyin envdan olib tashlash mumkin)
user.set_password(password)
changed = True

if created or changed:
    user.save()

print(f"Superuser tayyor: {username} (created={created})")
PY
fi
