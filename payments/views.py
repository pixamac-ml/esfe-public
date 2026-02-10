# payments/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import FileResponse, Http404

from inscriptions.models import Inscription
from payments.models import Payment
from payments.forms import StudentPaymentForm


# ==================================================
# DEMANDE DE PAIEMENT (ÉTUDIANT – LIEN PUBLIC)
# ==================================================
def student_initiate_payment(request, token):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages

    inscription = get_object_or_404(
        Inscription,
        public_token=token
    )

    if request.method != "POST":
        return redirect(inscription.get_public_url())

    form = StudentPaymentForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Formulaire invalide."
        )
        return redirect(inscription.get_public_url())

    amount = form.cleaned_data["amount"]
    method = form.cleaned_data["method"]

    if amount <= 0:
        messages.error(request, "Montant invalide.")
        return redirect(inscription.get_public_url())

    if amount > inscription.balance:
        messages.error(request, "Le montant dépasse le solde restant.")
        return redirect(inscription.get_public_url())

    if inscription.payments.filter(status="pending").exists():
        messages.warning(
            request,
            "Un paiement est déjà en attente de validation."
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
# AFFICHAGE PUBLIC D’UN REÇU
# ==================================================
def receipt_public_detail(request, receipt_number):
    payment = get_object_or_404(
        Payment,
        receipt_number=receipt_number,
        status="validated"
    )

    inscription = payment.inscription

    return render(
        request,
        "payments/receipt_detail.html",
        {
            "payment": payment,
            "inscription": inscription,
            "candidature": inscription.candidature,
            "programme": inscription.candidature.programme,
        }
    )


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
        raise Http404("Le reçu PDF n’est pas disponible.")

    return FileResponse(
        payment.receipt_pdf.open("rb"),
        as_attachment=True,
        filename=f"recu-{payment.receipt_number}.pdf"
    )
