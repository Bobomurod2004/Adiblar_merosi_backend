def safe_media_url(file_field):
    """
    File/Image field URL ni xavfsiz qaytaradi.
    Agar fayl DB da bor, lekin storage'da yo'q bo'lsa None qaytaradi.
    """
    if not file_field:
        return None

    name = getattr(file_field, 'name', '')
    if not name:
        return None

    try:
        storage = getattr(file_field, 'storage', None)
        if storage and not storage.exists(name):
            return None
        return file_field.url
    except Exception:
        return None
