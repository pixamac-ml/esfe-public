# payments/views.py
from payments.forms import StudentPaymentForm

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.contrib import messages
from django.http import FileResponse, Http404

from inscriptions.models import Inscription
from .models import Payment


# ==================================================
# INITIER UN PAIEMENT (étudiant)
# ==================================================
def initiate_payment(request, reference):
    """
    Création d’une demande de paiement (pending).
    - Un seul paiement pending autorisé à la fois
    - Montant = solde restant
    """

    inscription = get_object_or_404(Inscription, reference=reference)

    if request.method == "POST":

        # 🔒 Bloquer s’il existe déjà un paiement en attente
        if Payment.objects.filter(
            inscription=inscription,
            status="pending"
        ).exists():
            messages.warning(
                request,
                "Une demande de paiement est déjà en cours de traitement."
            )
            return redirect(inscription.get_public_url())

        amount = inscription.balance

        if amount <= 0:
            messages.info(
                request,
                "Aucun montant restant à payer."
            )
            return redirect(inscription.get_public_url())

        Payment.objects.create(
            inscription=inscription,
            amount=amount,
            method="cash",              # mode test
            status="pending",
            reference="INITIATED_BY_STUDENT"
        )

        messages.success(
            request,
            "Votre demande de paiement a été enregistrée. "
            "Veuillez finaliser auprès de l’administration."
        )

    return redirect(inscription.get_public_url())


# ==================================================
# DÉTAIL PUBLIC D’UN REÇU (basé sur Payment)
# ==================================================
def receipt_public_detail(request, receipt_number):
    """
    Affichage public du reçu (HTML).
    Basé sur Payment.validated + receipt_number.
    """

    payment = get_object_or_404(
        Payment,
        receipt_number=receipt_number,
        status="validated"
    )

    inscription = payment.inscription
    candidature = inscription.candidature
    programme = candidature.programme

    return render(
        request,
        "payments/receipt_detail.html",
        {
            "payment": payment,
            "inscription": inscription,
            "candidature": candidature,
            "programme": programme,
        }
    )


# ==================================================
# TÉLÉCHARGEMENT PDF DU REÇU
# ==================================================

# payments/views.py
def student_initiate_payment(request, token):
    inscription = get_object_or_404(
        Inscription,
        public_token=token
    )

    form = StudentPaymentForm(request.POST)

    if form.is_valid():
        amount = form.cleaned_data["amount"]
        method = form.cleaned_data["method"]

        if amount > inscription.balance:
            messages.error(
                request,
                "Le montant dépasse le solde restant."
            )
            return redirect(inscription.get_public_url())

        if inscription.payments.filter(status="pending").exists():
            messages.warning(
                request,
                "Une demande de paiement est déjà en cours."
            )
            return redirect(inscription.get_public_url())

        Payment.objects.create(
            inscription=inscription,
            amount=amount,
            method=method,
            status="pending",
            reference="INITIATED_BY_STUDENT"
        )

        messages.success(
            request,
            "Votre demande de paiement a été transmise à l’administration."
        )

    return redirect(inscription.get_public_url())


# ==================================================
# TÉLÉCHARGEMENT DU REÇU PDF
# ==================================================
def receipt_pdf(request, receipt_number):
    payment = get_object_or_404(
        Payment,
        receipt_number=receipt_number,
        status="validated"
    )

    if not payment.receipt_pdf:
        raise Http404("Reçu non disponible.")

    return FileResponse(
        payment.receipt_pdf.open("rb"),
        as_attachment=True,
        filename=f"recu-{payment.receipt_number}.pdf"
    )
