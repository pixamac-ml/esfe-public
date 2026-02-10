from django.shortcuts import get_object_or_404, render
from inscriptions.models import Inscription
from payments.forms import StudentPaymentForm


def inscription_public_detail(request, token):
    inscription = get_object_or_404(
        Inscription,
        public_token=token
    )

    payments = inscription.payments.order_by("-created_at")

    context = {
        "inscription": inscription,
        "candidature": inscription.candidature,
        "programme": inscription.candidature.programme,

        # 🔹 Historique
        "payments": payments,

        # 🔹 Formulaire étudiant
        "payment_form": StudentPaymentForm(),

        # 🔹 Dernier reçu validé
        "receipt_payment": (
            payments
            .filter(status="validated", receipt_number__isnull=False)
            .order_by("-paid_at")
            .first()
        ),
    }

    return render(
        request,
        "inscriptions/public_detail.html",
        context
    )
