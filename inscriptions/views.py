from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .models import Enrollment


def finalize_enrollment(request, token):
    """
    Vue publique de finalisation d'inscription.
    Accessible via lien sécurisé (public_token).

    Règles métier :
    - lien toujours accessible
    - paiement possible tant que l'inscription n'est pas activée
    """

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "application__candidate",
            "application__programme",
            "academic_year",
        ).prefetch_related(
            "fees__payments",
            "fees__template",
        ),
        public_token=token
    )

    # ==================================================
    # CAS BLOQUANTS
    # ==================================================
    if enrollment.status == Enrollment.STATUS_CANCELLED:
        return render(request, "inscriptions/finalize_blocked.html", {
            "message": (
                "Cette inscription a été annulée. "
                "Veuillez contacter l'administration."
            )
        })

    if enrollment.status == Enrollment.STATUS_SUSPENDED:
        return render(request, "inscriptions/finalize_blocked.html", {
            "message": (
                "Cette inscription est suspendue. "
                "Veuillez contacter l'administration."
            )
        })

    # ==================================================
    # CAS INSCRIPTION DÉJÀ FINALISÉE
    # ==================================================
    if enrollment.is_active:
        return render(request, "inscriptions/finalize_done.html", {
            "enrollment": enrollment,
        })

    # ==================================================
    # CALCUL FINANCIER CENTRALISÉ
    # ==================================================
    fees = enrollment.fees.all()

    total_expected = sum(
        fee.amount_to_pay for fee in fees
    )

    total_paid = sum(
        fee.total_paid for fee in fees
    )

    remaining_amount = max(total_expected - total_paid, 0)

    # ==================================================
    # AFFICHAGE STANDARD (PAIEMENT / CONTINUATION)
    # ==================================================
    context = {
        "enrollment": enrollment,
        "fees": fees,
        "total_expected": total_expected,
        "total_paid": total_paid,
        "remaining_amount": remaining_amount,
        "can_pay": remaining_amount > 0,
    }

    return render(
        request,
        "inscriptions/finalize_enrollment.html",
        context
    )
