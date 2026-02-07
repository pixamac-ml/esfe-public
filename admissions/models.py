from django.db import models
from django.utils import timezone
from formations.models import Programme, RequiredDocument


# --------------------------------------------------
# CANDIDAT
# --------------------------------------------------
class Candidate(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    birth_date = models.DateField()
    birth_place = models.CharField(max_length=150)

    phone = models.CharField(max_length=30)
    email = models.EmailField(unique=True)

    address = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


# --------------------------------------------------
# CANDIDATURE (DOSSIER ACADÉMIQUE)
# --------------------------------------------------
class Application(models.Model):
    STATUS_SUBMITTED = "submitted"
    STATUS_UNDER_REVIEW = "under_review"
    STATUS_INCOMPLETE = "incomplete"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, "Soumise"),
        (STATUS_UNDER_REVIEW, "En étude"),
        (STATUS_INCOMPLETE, "Dossier incomplet"),
        (STATUS_ACCEPTED, "Acceptée"),
        (STATUS_REJECTED, "Refusée"),
    ]

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT,
        related_name="applications"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED
    )

    motivation = models.TextField(
        blank=True,
        help_text="Lettre ou texte de motivation du candidat"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        unique_together = ("candidate", "programme")
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return f"{self.candidate} → {self.programme.title}"

    # -------------------------
    # PROPRIÉTÉS MÉTIER
    # -------------------------
    @property
    def is_complete(self) -> bool:
        """
        Une candidature est complète si tous les documents requis
        ont été fournis ET validés.
        """
        required_docs = RequiredDocument.objects.filter(
            programrequireddocument__programme=self.programme
        )

        if not required_docs.exists():
            return True  # Aucun document requis

        validated_docs = self.documents.filter(
            is_valid=True
        ).values_list("document_id", flat=True)

        return required_docs.filter(
            id__in=validated_docs
        ).count() == required_docs.count()

    # -------------------------
    # MÉTHODES MÉTIER
    # -------------------------
    def mark_under_review(self):
        self.status = self.STATUS_UNDER_REVIEW
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_at"])

    def accept(self):
        """
        Accepte la candidature SI ET SEULEMENT SI le dossier est complet.
        """
        if not self.is_complete:
            raise ValueError("Le dossier n'est pas complet.")

        if self.status == self.STATUS_ACCEPTED:
            return  # idempotence

        self.status = self.STATUS_ACCEPTED
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_at"])

    def reject(self):
        self.status = self.STATUS_REJECTED
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_at"])

    def mark_incomplete(self):
        self.status = self.STATUS_INCOMPLETE
        self.save(update_fields=["status"])


# --------------------------------------------------
# DOCUMENT DE CANDIDATURE
# --------------------------------------------------
class ApplicationDocument(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document = models.ForeignKey(
        RequiredDocument,
        on_delete=models.PROTECT
    )

    file = models.FileField(
        upload_to="admissions/documents/"
    )

    is_valid = models.BooleanField(
        null=True,
        help_text="Validé par l'administration"
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("application", "document")
        ordering = ["uploaded_at"]

    def __str__(self):
        return f"{self.document.name} – {self.application}"

    def validate(self):
        self.is_valid = True
        self.save(update_fields=["is_valid"])

    def invalidate(self):
        self.is_valid = False
        self.save(update_fields=["is_valid"])
