from django.db import models
from django.contrib.auth.models import User

from inscriptions.models import Inscription


class Student(models.Model):
    """
    Étudiant officiellement inscrit à l’ESFE.
    Créé après validation du premier paiement.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="student_profile"
    )

    inscription = models.OneToOneField(
        Inscription,
        on_delete=models.PROTECT,
        related_name="student"
    )

    matricule = models.CharField(
        max_length=30,
        unique=True
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Accès à la plateforme pédagogique"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.matricule}"
