from django.utils import timezone

def generate_receipt_number(payment):
    year = timezone.now().year
    return f"ESFE-{year}-{payment.pk:06d}"
