# payments/models.py

from django.db import models, transaction
from django.utils import timezone
from django.core.files.base import ContentFile

from inscriptions.models import Inscription
from payments.services.receipt import generate_receipt_number
from payments.services.qrcode import generate_qr_image
from payments.utils.pdf import render_pdf

from students.services.create_student import (
    create_student_after_first_payment
)
from students.services.email import send_student_credentials_email


class Payment(models.Model):
    """
    Paiement lié à une inscription.

    RÈGLES MÉTIER (STRICTES) :
    - Un paiement VALIDÉ :
        • met à jour l’inscription (montant payé / statut)
        • génère UN SEUL reçu PDF
        • crée le compte étudiant au PREMIER paiement validé
    - AUCUN signal métier
    - TOUT est centralisé ici
    """

    # ==================================================
    # CHOIX
    # ==================================================
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

    # ==================================================
    # LIENS
    # ==================================================
    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    # ==================================================
    # DONNÉES DE PAIEMENT
    # ==================================================
    amount = models.PositiveIntegerField(
        help_text="Montant payé en FCFA"
    )

    method = models.CharField(
        max_length=30,
        choices=METHOD_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Référence externe (OM, virement, reçu manuel)"
    )

    # ==================================================
    # REÇU
    # ==================================================
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True
    )

    receipt_pdf = models.FileField(
        upload_to="payments/receipts/",
        null=True,
        blank=True
    )

    # ==================================================
    # MÉTADONNÉES
    # ==================================================
    paid_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["method"]),
            models.Index(fields=["paid_at"]),
        ]

    def __str__(self):
        return f"{self.amount} FCFA – {self.inscription.reference}"

    # ==================================================
    # PIPELINE MÉTIER CENTRAL
    # ==================================================
    def save(self, *args, **kwargs):
        """
        PIPELINE STRICT :

        1️⃣ Détection du passage → VALIDATED
        2️⃣ Mise à jour financière de l’inscription
        3️⃣ Génération du reçu (UNE FOIS)
        4️⃣ Création étudiant + email (APRÈS COMMIT)
        """

        previous_status = None
        if self.pk:
            previous_status = Payment.objects.get(pk=self.pk).status

        with transaction.atomic():
            super().save(*args, **kwargs)

            just_validated = (
                self.status == "validated"
                and previous_status != "validated"
            )

            if not just_validated:
                return

            # ---------------------------------------------
            # 1️⃣ SYNCHRONISATION FINANCIÈRE
            # ---------------------------------------------
            self.inscription.update_financial_state()

            # ---------------------------------------------
            # 2️⃣ GÉNÉRATION DU REÇU (UNE SEULE FOIS)
            # ---------------------------------------------
            if not self.receipt_number:
                self.receipt_number = generate_receipt_number(self)

                qr_image = generate_qr_image(
                    self.inscription.get_public_url()
                )

                pdf_bytes = render_pdf(
                    payment=self,
                    inscription=self.inscription,
                    qr_image=qr_image
                )

                self.receipt_pdf.save(
                    f"receipt-{self.receipt_number}.pdf",
                    ContentFile(pdf_bytes),
                    save=False
                )

                super().save(
                    update_fields=["receipt_number", "receipt_pdf"]
                )

        # ---------------------------------------------
        # 3️⃣ CRÉATION ÉTUDIANT (APRÈS COMMIT)
        # ---------------------------------------------
        result = create_student_after_first_payment(self.inscription)

        if result:
            send_student_credentials_email(
                student=result["student"],
                raw_password=result["password"]
            )
