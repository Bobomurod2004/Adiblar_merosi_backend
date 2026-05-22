import mimetypes
import posixpath
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile, File
from django.core.files.storage import Storage
from django.core.files.utils import validate_file_name
from django.utils.deconstruct import deconstructible
from supabase import Client, create_client


@deconstructible
class SupabaseStorage(Storage):
    """
    Django media fayllarini Supabase Storage ga saqlash backend'i.
    """

    def __init__(self):
        self._client: Optional[Client] = None
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
        self.path_prefix = getattr(settings, "SUPABASE_MEDIA_PREFIX", "").strip("/")
        self.cache_control = str(getattr(settings, "SUPABASE_MEDIA_CACHE_CONTROL", "3600"))
        self.upsert = str(getattr(settings, "SUPABASE_MEDIA_UPSERT", "false")).lower()
        self.bucket_public = bool(getattr(settings, "SUPABASE_BUCKET_PUBLIC", True))
        self.signed_url_expires = int(getattr(settings, "SUPABASE_SIGNED_URL_EXPIRES", 3600))

    @property
    def client(self) -> Client:
        if self._client is None:
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_KEY
            if not url or not key:
                raise RuntimeError("SUPABASE_URL va SUPABASE_KEY/SUPABASE_SERVICE_ROLE_KEY majburiy.")
            self._client = create_client(url, key)
        return self._client

    @property
    def bucket(self):
        return self.client.storage.from_(self.bucket_name)

    def _clean_name(self, name: str) -> str:
        cleaned = validate_file_name(name, allow_relative_path=True).replace("\\", "/").lstrip("/")
        if self.path_prefix:
            return posixpath.join(self.path_prefix, cleaned)
        return cleaned

    def _content_type_for(self, name: str, content) -> str:
        content_type = getattr(content, "content_type", None)
        if content_type:
            return str(content_type)
        guessed, _ = mimetypes.guess_type(name)
        return guessed or "application/octet-stream"

    def _open(self, name: str, mode: str = "rb") -> File:
        # Supabase API bytes qaytaradi; Django File bilan o'rab qaytaramiz.
        cleaned = self._clean_name(name)
        data = self.bucket.download(cleaned)
        return File(ContentFile(data), name=name)

    def _save(self, name: str, content) -> str:
        cleaned = self._clean_name(name)
        upload_source = getattr(content, "file", content)
        if hasattr(upload_source, "seek"):
            upload_source.seek(0)

        # supabase-py upload() hamma file-like turlarni qabul qilmaydi.
        # Django upload obyektlarini bytes ga aylantirib yuborish eng barqaror yo'l.
        if hasattr(upload_source, "read"):
            payload = upload_source.read()
        else:
            payload = content.read()

        if isinstance(payload, str):
            payload = payload.encode("utf-8")

        self.bucket.upload(
            path=cleaned,
            file=payload,
            file_options={
                "cache-control": self.cache_control,
                "content-type": self._content_type_for(cleaned, content),
                "upsert": self.upsert,
            },
        )
        return name

    def delete(self, name: str) -> None:
        if not name:
            return
        cleaned = self._clean_name(name)
        try:
            self.bucket.remove([cleaned])
        except Exception:
            # File allaqachon yo'q bo'lsa yoki remote tomonda xatolik bo'lsa
            # delete() django contracti bo'yicha sokin ishlashi kerak.
            return

    def exists(self, name: str) -> bool:
        cleaned = self._clean_name(name)
        try:
            return bool(self.bucket.exists(cleaned))
        except Exception:
            # Ba'zi storage policy holatlarida exists() uchun select ruxsati bo'lmaydi.
            # Bunday vaziyatda nom bo'sh deb hisoblaymiz va uploadni davom ettiramiz.
            return False

    def size(self, name: str) -> int:
        cleaned = self._clean_name(name)
        info = self.bucket.info(cleaned)
        metadata = info.get("metadata") or {}
        raw_size = metadata.get("size") or info.get("size")
        try:
            return int(raw_size)
        except (TypeError, ValueError):
            return 0

    def url(self, name: str) -> str:
        cleaned = self._clean_name(name)
        if self.bucket_public:
            return self.bucket.get_public_url(cleaned)

        signed = self.bucket.create_signed_url(cleaned, self.signed_url_expires)
        return signed.get("signedURL") or signed.get("signedUrl") or self.bucket.get_public_url(cleaned)
