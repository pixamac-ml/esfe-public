from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.files.base import ContentFile

def render_pdf(template, context):
    html = render_to_string(template, context)
    pdf = HTML(string=html).write_pdf()
    return ContentFile(pdf)
