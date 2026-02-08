from django.db import models, transaction
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
        """
        GARANTIE MÉTIER :
        Une seule année académique peut être active à la fois.
        """
        with transaction.atomic():
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
    # STATUTS ADMINISTRATIFS (HUMAINS)
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
        null=True,
        help_text="Généré automatiquement après activation"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    enrolled_at = models.DateTimeField(default=timezone.now)

    validated_at = models.DateTimeField(null=True, blank=True)

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

    # -------------------------
    # ÉTAT SYSTÈME (AUTOMATIQUE)
    # -------------------------
    is_active = models.BooleanField(
        default=False,
        help_text="Autorise l'accès à la plateforme pédagogique"
    )

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
    # MÉTHODES MÉTIER (HUMAINES)
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

    # ==================================================
    # MÉTHODES MÉTIER (AUTOMATIQUES)
    # ==================================================
    def activate(self):
        """
        Activation AUTOMATIQUE après paiement requis.
        """
        if self.is_active or self.status == self.STATUS_CANCELLED:
            return

        with transaction.atomic():
            self.is_active = True
            self.finalized_at = timezone.now()

            if not self.matricule:
                self.matricule = self._generate_matricule_safe()

            self.save(update_fields=["is_active", "finalized_at", "matricule"])

    def _generate_matricule_safe(self):
        """
        Génération SÛRE du matricule (thread-safe).
        Exemple : ESFE-2025-000123
        """
        year = self.academic_year.label.split("-")[0]

        last_enrollment = (
            Enrollment.objects
            .select_for_update()
            .filter(
                academic_year=self.academic_year,
                matricule__isnull=False
            )
            .order_by("-created_at")
            .first()
        )

        last_number = (
            int(last_enrollment.matricule.split("-")[-1])
            if last_enrollment else 0
        )

        new_number = last_number + 1

        return f"ESFE-{year}-{str(new_number).zfill(6)}"
