# payments/models.py
from django.db import models
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
