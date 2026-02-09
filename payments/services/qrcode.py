import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_code(url):
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())
