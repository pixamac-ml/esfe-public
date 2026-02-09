# inscriptions/models.py
import uuid

from django.db import models
from django.urls import reverse

from admissions.models import Candidature


class Inscription(models.Model):
    # --------------------------------------------------
    # LIEN MÉTIER
    # --------------------------------------------------
    candidature = models.OneToOneField(
        Candidature,
        on_delete=models.PROTECT,
        related_name="inscription"
    )

    # --------------------------------------------------
    # IDENTIFIANT PUBLIC
    # --------------------------------------------------
    reference = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    # --------------------------------------------------
    # STATUT
    # --------------------------------------------------
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

    # --------------------------------------------------
    # FINANCES
    # --------------------------------------------------
    amount_due = models.PositiveIntegerField(
        default=0,
        help_text="Montant total à payer pour l’inscription (FCFA)"
    )

    amount_paid = models.PositiveIntegerField(
        default=0,
        help_text="Montant déjà payé (FCFA)"
    )

    # --------------------------------------------------
    # MÉTADONNÉES
    # --------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)

    # --------------------------------------------------
    # CONFIG
    # --------------------------------------------------
    class Meta:
        ordering = ["-created_at"]

    # --------------------------------------------------
    # MÉTHODES
    # --------------------------------------------------
    def __str__(self):
        return f"Inscription – {self.candidature} – {self.reference}"

    def get_public_url(self):
        return reverse(
            "inscriptions:public_detail",
            kwargs={"reference": self.reference}
        )

    @property
    def balance(self):
        return max(self.amount_due - self.amount_paid, 0)

    @property
    def is_paid(self):
        return self.amount_paid >= self.amount_due
