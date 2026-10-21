"""
Seller product photos. A photo is checked with Pillow (it must really be an image), resized to at most 1200 px and saved as JPEG
under media/product_images with a random name, so a seller can never overwrite another file or upload something that is not a picture.
"""

import io
import uuid

from django.conf import settings
from django.http import Http404, HttpResponse
from PIL import Image, UnidentifiedImageError

MAX_BYTES = 5 * 1024 * 1024
DIR = settings.MEDIA_ROOT / 'product_images'


def save_photo(upload, request):
    """Returns (public_url, error). Exactly one of the two is set."""
    if upload.size > MAX_BYTES:
        return None, 'That photo is larger than 5 MB. Please choose a smaller one.'
    try:
        img = Image.open(io.BytesIO(upload.read()))
        img.verify()
        upload.seek(0)
        img = Image.open(io.BytesIO(upload.read())).convert('RGB')
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):  # Pillow raises SyntaxError for a damaged PNG
        return None, 'That file is not a picture. Please upload a JPG, PNG or WebP photo.'
    img.thumbnail((1200, 1200))
    DIR.mkdir(parents=True, exist_ok=True)
    name = f'{uuid.uuid4().hex}.jpg'
    img.save(DIR / name, 'JPEG', quality=86, optimize=True)
    return request.build_absolute_uri(f'/api/media/product_images/{name}'), None


def serve_photo(request, name):
    path = (DIR / name).resolve()
    if DIR.resolve() not in path.parents or not path.is_file():
        raise Http404()
    resp = HttpResponse(path.read_bytes(), content_type='image/jpeg')
    resp['Cache-Control'] = 'public, max-age=86400'
    return resp
