from django.db import transaction
from inscriptions.models import Enrollment, AcademicYear
from payments.models import FeeTemplate, Fee


def prepare_enrollment(application):
    """
    Prépare l'inscription administrative et les frais
    APRÈS acceptation de la candidature.
    """

    # Sécurité : déjà préparée
    if hasattr(application, "enrollment"):
        return application.enrollment

    academic_year = AcademicYear.objects.filter(is_active=True).first()
    if not academic_year:
        raise RuntimeError("Aucune année académique active.")

    with transaction.atomic():

        enrollment = Enrollment.objects.create(
            application=application,
            academic_year=academic_year,
            status=Enrollment.STATUS_PENDING,
            is_active=False,
        )

        fee_templates = FeeTemplate.objects.filter(
            programme=application.programme,
            is_active=True
        ).order_by("order")

        if not fee_templates.exists():
            raise RuntimeError(
                f"Aucun frais défini pour {application.programme}"
            )

        for template in fee_templates:
            Fee.objects.create(
                enrollment=enrollment,
                template=template,
                amount_expected=template.amount
            )

    return enrollment
