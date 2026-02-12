# payments/views.py

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import FileResponse, Http404, JsonResponse

from inscriptions.models import Inscription
from payments.models import Payment, PaymentAgent
from payments.forms import StudentPaymentForm


# ==================================================
# DEMANDE DE PAIEMENT (ÉTUDIANT – LIEN PUBLIC)
# ==================================================
def student_initiate_payment(request, token):

    inscription = get_object_or_404(
        Inscription,
        public_token=token
    )

    if request.method != "POST":
        return redirect(inscription.get_public_url())

    form = StudentPaymentForm(
        request.POST,
        inscription=inscription
    )

    # ==============================
    # FORMULAIRE INVALIDE
    # ==============================
    if not form.is_valid():
        payments = inscription.payments.order_by("-paid_at")

        context = {
            "inscription": inscription,
            "candidature": inscription.candidature,
            "programme": inscription.candidature.programme,
            "payments": payments,
            "payment_form": form,
            "can_pay": True,
            "has_pending_payment": False,
        }

        return render(
            request,
            "inscriptions/public_detail.html",
            context
        )

    amount = form.cleaned_data["amount"]
    method = form.cleaned_data["method"]

    # ==============================
    # SÉCURITÉ MÉTIER
    # ==============================
    if amount > inscription.balance:
        messages.error(request, "Le montant dépasse le solde restant.")
        return redirect(inscription.get_public_url())

    if inscription.payments.filter(status="pending").exists():
        messages.warning(
            request,
            "Un paiement est déjà en attente de validation."
        )
        return redirect(inscription.get_public_url())

    # ==============================
    # CRÉATION PAIEMENT
    # ==============================
    payment_data = {
        "inscription": inscription,
        "amount": amount,
        "method": method,
        "status": "pending",
        "reference": "INITIATED_BY_STUDENT",
    }

    # Si paiement cash → rattacher agent
    if method == "cash":
        payment_data["agent"] = form.agent

    Payment.objects.create(**payment_data)

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


# ==================================================
# AJAX – VÉRIFICATION AGENT
# ==================================================
def verify_agent_ajax(request):
    """
    Vérifie dynamiquement si un agent existe.
    Recherche robuste prénom + nom.
    """

    name = request.GET.get("name", "").strip()

    if not name:
        return JsonResponse({"valid": False})

    parts = name.split()

    queryset = PaymentAgent.objects.select_related("user").filter(
        is_active=True
    )

    # Recherche intelligente
    if len(parts) == 1:
        queryset = queryset.filter(
            user__first_name__iexact=parts[0]
        )
    elif len(parts) >= 2:
        queryset = queryset.filter(
            user__first_name__iexact=parts[0],
            user__last_name__iexact=parts[1]
        )

    agent = queryset.first()

    if not agent:
        return JsonResponse({"valid": False})

    return JsonResponse({
        "valid": True,
        "full_name": agent.user.get_full_name(),
        "agent_code": agent.agent_code,
    })
