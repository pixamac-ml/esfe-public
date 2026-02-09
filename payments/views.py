from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from inscriptions.models import Inscription
from .models import Payment


from django.db.models import Q

def initiate_payment(request, reference):
    inscription = get_object_or_404(Inscription, reference=reference)

    if request.method == "POST":

        # 🔒 BLOQUER SI UN PAIEMENT EN ATTENTE EXISTE DÉJÀ
        existing_payment = Payment.objects.filter(
            inscription=inscription,
            status="pending"
        ).first()

        if existing_payment:
            messages.warning(
                request,
                "Une demande de paiement est déjà en cours de traitement."
            )
            return redirect(inscription.get_public_url())

        amount = inscription.balance

        if amount <= 0:
            messages.info(request, "Aucun montant restant à payer.")
            return redirect(inscription.get_public_url())

        Payment.objects.create(
            inscription=inscription,
            amount=amount,
            method="cash",
            status="pending",
            reference="INITIATED_BY_STUDENT"
        )

        messages.success(
            request,
            "Votre demande de paiement a été enregistrée."
        )

    return redirect(inscription.get_public_url())
