import os
from pathlib import Path

from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.utils._os import safe_join


def normalize_media_name(value):
    """
    File nomini storage-relative holatga keltiradi:
    - leading slashni olib tashlaydi
    - /media/ yoki media/ prefiksini olib tashlaydi
    """
    raw = str(value or '').strip().replace('\\', '/')
    if not raw:
        return ''

    raw = raw.split('?', 1)[0].split('#', 1)[0]
    raw = raw.lstrip('/')

    media_prefix = str(getattr(settings, 'MEDIA_URL', '/media/')).strip('/')
    prefixes = [prefix for prefix in (media_prefix, 'media') if prefix]
    for prefix in prefixes:
        if raw == prefix:
            return ''
        prefix_with_slash = f'{prefix}/'
        if raw.startswith(prefix_with_slash):
            raw = raw[len(prefix_with_slash):]
            break

    return raw.lstrip('/')


def get_media_root_candidates():
    """Media faylni qidirish uchun barcha root papkalarni qaytaradi."""
    candidates = []

    configured_root = getattr(settings, 'MEDIA_ROOT', '')
    if configured_root:
        candidates.append(Path(configured_root))

    fallbacks_raw = os.environ.get('MEDIA_ROOT_FALLBACKS', '')
    for raw in fallbacks_raw.split(','):
        cleaned = raw.strip()
        if cleaned:
            candidates.append(Path(cleaned))

    base_dir = getattr(settings, 'BASE_DIR', None)
    root_dir = getattr(settings, 'ROOT_DIR', None)
    if base_dir:
        candidates.append(Path(base_dir) / 'media')
    if root_dir:
        candidates.append(Path(root_dir) / 'media')

    # Render persistent disk uchun keng tarqalgan joy.
    candidates.append(Path('/var/data/media'))

    unique_candidates = []
    seen = set()
    for path_obj in candidates:
        resolved = path_obj.expanduser().resolve(strict=False)
        key = str(resolved)
        if key in seen:
            continue
        seen.add(key)
        unique_candidates.append(resolved)
    return unique_candidates


def resolve_media_file_path(name):
    """Nisbiy media nomidan real mavjud fayl yo'lini topadi."""
    normalized_name = normalize_media_name(name)
    if not normalized_name:
        return None

    for root in get_media_root_candidates():
        try:
            absolute_path = Path(safe_join(str(root), normalized_name))
        except SuspiciousFileOperation:
            continue

        if absolute_path.exists() and absolute_path.is_file():
            return absolute_path

    return None


def safe_media_url(file_field):
    """
    File/Image field URL ni xavfsiz qaytaradi.
    Agar fayl DB da bor, lekin serverda topilmasa None qaytaradi.
    """
    if not file_field:
        return None

    raw_name = getattr(file_field, 'name', '')
    normalized_name = normalize_media_name(raw_name)
    if not normalized_name:
        return None

    media_url = str(getattr(settings, 'MEDIA_URL', '/media/'))
    if not media_url.endswith('/'):
        media_url = f'{media_url}/'

    def normalized_public_url():
        return f'{media_url}{normalized_name}'

    try:
        storage = getattr(file_field, 'storage', None)
        if storage and storage.exists(normalized_name):
            raw_url = getattr(file_field, 'url', '') or ''
            if raw_url.startswith('http://') or raw_url.startswith('https://'):
                return raw_url
            return normalized_public_url()
    except Exception:
        pass

    # Legacy deploylarda MEDIA_ROOT o'zgargan bo'lsa, fallback rootlardan ham tekshiramiz.
    if resolve_media_file_path(normalized_name):
        return normalized_public_url()

    return None
