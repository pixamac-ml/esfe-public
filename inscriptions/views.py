from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.utils import timezone

from .models import Enrollment
from payments.models import Fee, Payment


def finalize_enrollment(request, token):
    """
    Vue publique de finalisation d'inscription.
    Accessible via lien sécurisé (public_token).
    """

    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            "application__candidate",
            "application__programme",
            "academic_year",
        ).prefetch_related("fees__payments"),
        public_token=token
    )

    # -----------------------------
    # CAS BLOQUANTS
    # -----------------------------
    if enrollment.status == Enrollment.STATUS_CANCELLED:
        return render(request, "inscriptions/finalize_blocked.html", {
            "message": "Cette inscription a été annulée. Veuillez contacter l'administration."
        })

    if enrollment.status == Enrollment.STATUS_SUSPENDED:
        return render(request, "inscriptions/finalize_blocked.html", {
            "message": "Cette inscription est suspendue. Veuillez contacter l'administration."
        })

    # -----------------------------
    # CALCUL DE LA SITUATION FINANCIÈRE
    # -----------------------------
    fees = enrollment.fees.all()

    total_expected = sum(f.amount_to_pay for f in fees)
    total_paid = sum(
        p.amount_paid
        for f in fees
        for p in f.payments.filter(status="validated")
    )

    remaining_amount = max(total_expected - total_paid, 0)

    # -----------------------------
    # CAS INSCRIPTION DÉJÀ FINALISÉE
    # -----------------------------
    if enrollment.status == Enrollment.STATUS_VALIDATED:
        return render(request, "inscriptions/finalize_done.html", {
            "enrollment": enrollment,
            "total_paid": total_paid,
        })

    # -----------------------------
    # AFFICHAGE STANDARD (PAYER / CONTINUER)
    # -----------------------------
    context = {
        "enrollment": enrollment,
        "fees": fees,
        "total_expected": total_expected,
        "total_paid": total_paid,
        "remaining_amount": remaining_amount,
        "can_pay": remaining_amount > 0,
    }

    return render(request, "inscriptions/finalize_enrollment.html", context)
