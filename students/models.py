from django.db import models
from django.conf import settings
from django.utils import timezone


class StudentProfile(models.Model):
    """
    Profil étudiant officiel.
    Créé UNIQUEMENT quand l'inscription est activée.
    """

    enrollment = models.OneToOneField(
        "inscriptions.Enrollment",
        on_delete=models.PROTECT,
        related_name="student_profile"
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Étudiant actif dans le système"
    )

    activated_at = models.DateTimeField(
        default=timezone.now
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        candidate = self.enrollment.application.candidate
        return f"Étudiant – {candidate.last_name} {candidate.first_name}"
