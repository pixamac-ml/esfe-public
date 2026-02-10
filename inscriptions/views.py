# inscriptions/views.py

from django.shortcuts import get_object_or_404, render
from django.http import Http404

from inscriptions.models import Inscription
from payments.forms import StudentPaymentForm


def inscription_public_detail(request, token):
    """
    Vue publique sécurisée du dossier d’inscription.

    RÈGLES :
    - L’inscription DOIT exister
    - Une inscription suspendue n’est pas payable
    - Le formulaire n’apparaît que si un paiement est autorisé
    """

    inscription = get_object_or_404(
        Inscription,
        public_token=token
    )

    # 🔒 Inscription suspendue → accès lecture seule
    if inscription.status == "suspended":
        raise Http404("Ce dossier est temporairement indisponible.")

    # Historique des paiements (ordre logique)
    payments = (
        inscription.payments
        .order_by("-paid_at")
    )

    # Paiement en attente (blocage formulaire)
    has_pending_payment = payments.filter(status="pending").exists()

    # Autorisation de paiement
    can_pay = (
        inscription.status == "created"
        and inscription.balance > 0
        and not has_pending_payment
    )

    context = {
        "inscription": inscription,
        "candidature": inscription.candidature,
        "programme": inscription.candidature.programme,

        # Historique
        "payments": payments,

        # Formulaire étudiant (contrôlé)
        "payment_form": StudentPaymentForm() if can_pay else None,

        # Dernier reçu validé
        "receipt_payment": (
            payments
            .filter(status="validated", receipt_number__isnull=False)
            .first()
        ),

        # Flags de contrôle (optionnel pour le template)
        "can_pay": can_pay,
        "has_pending_payment": has_pending_payment,
    }

    return render(
        request,
        "inscriptions/public_detail.html",
        context
    )
