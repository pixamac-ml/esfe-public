from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

# ==================================================
# ANNÉE ACADÉMIQUE
# ==================================================
class AcademicYear(models.Model):
    """
    Année académique officielle.
    Ex : 2024-2025
    """

    label = models.CharField(
        max_length=20,
        unique=True,
        help_text="Ex: 2024-2025"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(
        default=False,
        help_text="Année académique en cours"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        # 🔒 Une seule année académique active à la fois
        if self.is_active:
            AcademicYear.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

# ==================================================
# INSCRIPTION ADMINISTRATIVE
# ==================================================
class Enrollment(models.Model):
    """
    Inscription administrative officielle.
    Préparée après acceptation de candidature.
    Activée UNIQUEMENT après paiement requis.
    """

    # -------------------------
    # STATUTS ADMINISTRATIFS
    # -------------------------
    STATUS_PENDING = "pending"
    STATUS_VALIDATED = "validated"
    STATUS_SUSPENDED = "suspended"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_VALIDATED, "Validée administrativement"),
        (STATUS_SUSPENDED, "Suspendue"),
        (STATUS_CANCELLED, "Annulée"),
    ]

    application = models.OneToOneField(
        "admissions.Application",
        on_delete=models.PROTECT,
        related_name="enrollment"
    )

    academic_year = models.ForeignKey(
        "inscriptions.AcademicYear",
        on_delete=models.PROTECT,
        related_name="enrollments"
    )

    matricule = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Généré automatiquement après activation"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    enrolled_at = models.DateTimeField(
        default=timezone.now
    )

    validated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_enrollments"
    )

    notes = models.TextField(
        blank=True,
        help_text="Observations administratives internes"
    )

    # 🔐 Accès pédagogique
    is_active = models.BooleanField(
        default=False,
        help_text="Autorise l'accès à la plateforme pédagogique"
    )

    # 🔗 Lien public de finalisation
    public_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'activation après paiement"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.matricule or 'Pré-inscription'} – {self.application.candidate}"

    # ==================================================
    # MÉTHODES MÉTIER
    # ==================================================

    def validate_admin(self, user=None):
        """
        Validation administrative HUMAINE.
        Ne donne PAS accès à la plateforme.
        """
        if self.status != self.STATUS_PENDING:
            return

        self.status = self.STATUS_VALIDATED
        self.validated_at = timezone.now()
        self.validated_by = user
        self.save(update_fields=["status", "validated_at", "validated_by"])

    def activate(self):
        """
        Activation AUTOMATIQUE après paiement requis.
        """
        if self.is_active:
            return

        self.is_active = True
        self.finalized_at = timezone.now()

        if not self.matricule:
            self.matricule = self.generate_matricule()

        self.save(update_fields=["is_active", "finalized_at", "matricule"])

    def suspend(self, reason=None):
        self.status = self.STATUS_SUSPENDED
        self.is_active = False
        if reason:
            self.notes = reason
        self.save(update_fields=["status", "is_active", "notes"])

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.is_active = False
        self.save(update_fields=["status", "is_active"])

    def generate_matricule(self):
        """
        Génération institutionnelle du matricule.
        Exemple : ESFE-2025-000123
        """
        year = self.academic_year.label.split("-")[0]
        count = Enrollment.objects.filter(
            academic_year=self.academic_year
        ).count() + 1

        return f"ESFE-{year}-{str(count).zfill(6)}"
