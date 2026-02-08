from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Candidature


@receiver(post_save, sender=Candidature)
def candidature_status_handler(sender, instance, created, **kwargs):
    """
    Signal déclenché à chaque sauvegarde d’une candidature.
    Objectif V1 :
    - détecter une acceptation
    - préparer le terrain pour l’inscription
    """

    # On ignore la création initiale
    if created:
        return

    # Cas métier : candidature acceptée
    if instance.status in ("accepted", "accepted_with_reserve"):
        # Pour l’instant, on TRACE seulement
        # (plus tard : création Inscription)
        print(
            f"[SIGNAL] Candidature acceptée : "
            f"{instance.first_name} {instance.last_name} "
            f"({instance.programme.title}) "
            f"à {timezone.now()}"
        )
