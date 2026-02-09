# payments/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

from inscriptions.models import Inscription


class Payment(models.Model):
    # ----------------------------------
    # CHOIX MÉTIER
    # ----------------------------------
    METHOD_CHOICES = (
        ("cash", "Espèces"),
        ("orange_money", "Orange Money"),
        ("bank_transfer", "Virement bancaire"),
    )

    STATUS_CHOICES = (
        ("pending", "En attente"),
        ("validated", "Validé"),
        ("cancelled", "Annulé"),
    )

    # ----------------------------------
    # LIEN INSCRIPTION
    # ----------------------------------
    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    # ----------------------------------
    # DONNÉES FINANCIÈRES
    # ----------------------------------
    amount = models.PositiveIntegerField(
        help_text="Montant demandé ou payé (FCFA)"
    )

    method = models.CharField(
        max_length=30,
        choices=METHOD_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"   # ✅ TOUJOURS pending au départ
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Référence (reçu, OM, virement, agent, etc.)"
    )

    # ----------------------------------
    # MÉTADONNÉES TEMPORELLES
    # ----------------------------------
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de création de la demande"
    )

    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de validation du paiement"
    )

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["method"]),
            models.Index(fields=["requested_at"]),
        ]

    def __str__(self):
        return (
            f"{self.amount} FCFA – "
            f"{self.get_method_display()} – "
            f"{self.get_status_display()}"
        )

    # --------------------------------------------------
    # MÉTHODE MÉTIER EXPLICITE (PRO)
    # --------------------------------------------------
    def validate(self):
        """
        Valide le paiement :
        - passe le statut à validated
        - renseigne la date
        - recalcule le total payé de l'inscription
        """
        if self.status == "validated":
            return

        with transaction.atomic():
            self.status = "validated"
            self.validated_at = timezone.now()
            self.save(update_fields=["status", "validated_at"])

            total_paid = (
                self.inscription.payments
                .filter(status="validated")
                .aggregate(models.Sum("amount"))["amount__sum"] or 0
            )

            self.inscription.amount_paid = total_paid
            self.inscription.save(update_fields=["amount_paid"])

    receipt_number = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        help_text="Numéro officiel du reçu"
    )

    receipt_pdf = models.FileField(
        upload_to="receipts/",
        blank=True,
        null=True
    )

    def get_receipt_url(self):
        return reverse(
            "payments:receipt",
            kwargs={"pk": self.pk}
        )



# payments/models.py
import uuid
from django.db import models
from django.utils import timezone

from .models import Payment  # ou import local si même fichier


class Receipt(models.Model):
    """
    Reçu officiel de paiement.
    Créé UNIQUEMENT lorsqu’un paiement est validé.
    """

    payment = models.OneToOneField(
        Payment,
        on_delete=models.PROTECT,
        related_name="receipt"
    )

    reference = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )

    issued_at = models.DateTimeField(default=timezone.now)

    issued_by = models.CharField(
        max_length=150,
        help_text="Agent ou système ayant généré le reçu"
    )

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["issued_at"]),
        ]

    def __str__(self):
        return f"Reçu {self.reference}"

    # ----------------------------
    # GÉNÉRATION RÉFÉRENCE
    # ----------------------------
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()
        super().save(*args, **kwargs)

    def generate_reference(self):
        """
        Format exemple :
        ESFE-2026-000123
        """
        year = timezone.now().year
        uid = str(uuid.uuid4()).split("-")[0].upper()
        return f"ESFE-{year}-{uid}"


from payments.services.receipt import generate_receipt_number
from payments.services.qrcode import generate_qr_code
from payments.utils.pdf import render_pdf

def save(self, *args, **kwargs):
    is_new = self.pk is None
    previous_status = None

    if self.pk:
        previous_status = Payment.objects.get(pk=self.pk).status

    super().save(*args, **kwargs)

    if self.status == "validated" and previous_status != "validated":
        self.receipt_number = generate_receipt_number(self)

        qr_file = generate_qr_code(
            self.inscription.get_public_url()
        )

        pdf = render_pdf(
            "payments/receipt.html",
            {
                "payment": self,
                "qr_code_url": self.inscription.get_public_url(),
            }
        )

        self.receipt_pdf.save(
            f"receipt-{self.receipt_number}.pdf",
            pdf,
            save=False
        )

        super().save(update_fields=["receipt_number", "receipt_pdf"])
