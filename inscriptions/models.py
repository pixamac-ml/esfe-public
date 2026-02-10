# inscriptions/models.py

import uuid
import secrets

from django.db import models
from django.urls import reverse
from django.db.models import Sum

from admissions.models import Candidature


class Inscription(models.Model):
    # ==================================================
    # LIEN MÉTIER
    # ==================================================
    candidature = models.OneToOneField(
        Candidature,
        on_delete=models.PROTECT,
        related_name="inscription"
    )

    # ==================================================
    # IDENTIFIANTS
    # ==================================================
    reference = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    # 🔐 Token public sécurisé (lien étudiant)
    public_token = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True
    )

    # ==================================================
    # STATUT
    # ==================================================
    STATUS_CHOICES = (
        ("created", "Créée"),
        ("active", "Active"),
        ("suspended", "Suspendue"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    # ==================================================
    # FINANCES (SOURCE DE VÉRITÉ)
    # ==================================================
    amount_due = models.PositiveIntegerField(
        default=0,
        help_text="Montant total à payer (FCFA)"
    )

    amount_paid = models.PositiveIntegerField(
        default=0,
        help_text="Montant déjà payé (FCFA)"
    )

    # ==================================================
    # MÉTADONNÉES
    # ==================================================
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    # ==================================================
    # MÉTHODES SYSTÈME
    # ==================================================
    def __str__(self):
        return f"Inscription – {self.candidature} – {self.public_token}"

    def save(self, *args, **kwargs):
        """
        Génère le token public UNE SEULE FOIS.
        Jamais régénéré automatiquement.
        """
        if not self.public_token:
            self.public_token = self.generate_public_token()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_public_token():
        """
        Token non prédictible, partageable.
        Exemple : ESFE-INS-k9F3L2Qp7T8Z
        """
        return f"ESFE-INS-{secrets.token_urlsafe(12)}"

    # ==================================================
    # URL PUBLIQUE MÉTIER
    # ==================================================
    def get_public_url(self):
        return reverse(
            "inscriptions:public_detail",
            kwargs={"token": self.public_token}
        )

    # ==================================================
    # LOGIQUE FINANCIÈRE CENTRALE (VÉRITÉ ABSOLUE)
    # ==================================================
    def recalculate_financials(self):
        """
        Recalcule la situation financière
        UNIQUEMENT à partir des paiements VALIDÉS.
        """

        total_paid = (
            self.payments
            .filter(status="validated")
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        self.amount_paid = total_paid

        if self.amount_paid >= self.amount_due:
            self.status = "active"

        self.save(update_fields=["amount_paid", "status"])

    # ==================================================
    # PROPRIÉTÉS
    # ==================================================
    @property
    def balance(self):
        return max(self.amount_due - self.amount_paid, 0)

    @property
    def is_paid(self):
        return self.amount_paid >= self.amount_due
