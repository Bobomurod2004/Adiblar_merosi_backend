import mimetypes

from django.http import FileResponse, Http404

from .media import resolve_media_file_path


def serve_media_file(request, path):
    """
    Media faylni bir nechta rootlardan izlab, topilganini qaytaradi.
    Bu deploylarda MEDIA_ROOT o'zgarib qolgan holatlarni ham qoplaydi.
    """
    file_path = resolve_media_file_path(path)
    if file_path is None:
        raise Http404('Media file not found.')

    content_type, _ = mimetypes.guess_type(str(file_path))
    response = FileResponse(open(file_path, 'rb'))
    if content_type:
        response['Content-Type'] = content_type
    return response
