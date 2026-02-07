from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal


# ==================================================
# MODÈLE DE FRAIS (RÈGLE INSTITUTIONNELLE)
# ==================================================
class FeeTemplate(models.Model):
    """
    Règle officielle de frais liée à une formation.
    Ex : Frais d’inscription, Tranche 1, Tranche 2
    """

    FEE_TYPE_REGISTRATION = "registration"
    FEE_TYPE_TUITION = "tuition"
    FEE_TYPE_OTHER = "other"

    FEE_TYPE_CHOICES = [
        (FEE_TYPE_REGISTRATION, "Frais d’inscription"),
        (FEE_TYPE_TUITION, "Frais de scolarité"),
        (FEE_TYPE_OTHER, "Autres frais"),
    ]

    programme = models.ForeignKey(
        "formations.Programme",
        on_delete=models.PROTECT,
        related_name="fee_templates"
    )

    label = models.CharField(
        max_length=255,
        help_text="Ex : Frais d’inscription, Tranche Janvier"
    )

    fee_type = models.CharField(
        max_length=30,
        choices=FEE_TYPE_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Ordre logique de paiement"
    )

    is_mandatory = models.BooleanField(
        default=True,
        help_text="Obligatoire pour activer l’inscription"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Désactiver sans supprimer"
    )

    class Meta:
        ordering = ["order"]
        unique_together = ("programme", "label")

    def __str__(self):
        return f"{self.programme.title} – {self.label} ({self.amount} FCFA)"


# ==================================================
# FRAIS CONCRET (POUR UNE INSCRIPTION)
# ==================================================
class Fee(models.Model):
    """
    Frais appliqué à une inscription précise.
    Peut être réglé en plusieurs paiements.
    """

    enrollment = models.ForeignKey(
        "inscriptions.Enrollment",
        on_delete=models.CASCADE,
        related_name="fees"
    )

    template = models.ForeignKey(
        FeeTemplate,
        on_delete=models.PROTECT,
        related_name="fees"
    )

    amount_expected = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    amount_override = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Montant exceptionnel (réduction, arrangement)"
    )

    is_settled = models.BooleanField(
        default=False,
        help_text="Frais totalement réglé"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ("enrollment", "template")

    # -------------------------
    # PROPRIÉTÉS MÉTIER
    # -------------------------
    @property
    def amount_to_pay(self) -> Decimal:
        return (
            self.amount_override
            if self.amount_override is not None
            else self.amount_expected
        )

    @property
    def total_paid(self) -> Decimal:
        return sum(
            (p.amount_paid for p in self.payments.filter(status=Payment.STATUS_VALIDATED)),
            Decimal("0.00")
        )

    @property
    def remaining_amount(self) -> Decimal:
        remaining = self.amount_to_pay - self.total_paid
        return max(remaining, Decimal("0.00"))

    def recalculate_status(self) -> bool:
        """
        Recalcule l'état du frais.
        Retourne True si le frais est désormais soldé.
        """
        if self.total_paid >= self.amount_to_pay:
            if not self.is_settled:
                self.is_settled = True
                self.save(update_fields=["is_settled"])
            return True
        return False

    def __str__(self):
        return f"{self.template.label} – {self.amount_to_pay} FCFA"


# ==================================================
# PAIEMENT
# ==================================================
class Payment(models.Model):
    """
    Paiement individuel (partiel ou total).
    Déclenche les automatisations métier.
    """

    STATUS_PENDING = "pending"
    STATUS_VALIDATED = "validated"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_VALIDATED, "Validé"),
        (STATUS_REJECTED, "Rejeté"),
    ]

    METHOD_CASH = "cash"
    METHOD_MOBILE = "mobile_money"
    METHOD_BANK = "bank"
    METHOD_ONLINE = "online"

    METHOD_CHOICES = [
        (METHOD_CASH, "Espèces"),
        (METHOD_MOBILE, "Mobile Money"),
        (METHOD_BANK, "Virement bancaire"),
        (METHOD_ONLINE, "Paiement en ligne"),
    ]

    fee = models.ForeignKey(
        Fee,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    method = models.CharField(
        max_length=30,
        choices=METHOD_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    reference = models.CharField(
        max_length=150,
        blank=True,
        help_text="Reçu, référence Mobile Money, transaction bancaire"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_payments"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    # -------------------------
    # VALIDATIONS
    # -------------------------
    def clean(self):
        if self.amount_paid <= 0:
            raise ValidationError("Le montant payé doit être supérieur à zéro.")

        if self.fee.is_settled:
            raise ValidationError("Ce frais est déjà soldé.")

        if self.amount_paid > self.fee.remaining_amount:
            raise ValidationError(
                f"Le montant dépasse le reste à payer ({self.fee.remaining_amount} FCFA)."
            )

    # -------------------------
    # MÉTHODES MÉTIER
    # -------------------------
    def validate(self, user=None):
        """
        Valide officiellement le paiement.
        Déclenche les recalculs métier.
        """
        if self.status != self.STATUS_PENDING:
            return

        self.status = self.STATUS_VALIDATED
        self.validated_by = user
        self.paid_at = timezone.now()
        self.full_clean()
        self.save()

    def __str__(self):
        return f"{self.amount_paid} FCFA – {self.get_status_display()}"
