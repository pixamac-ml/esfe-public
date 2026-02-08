from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Application
from admissions.services import prepare_enrollment


# ==================================================
# SIGNAL DE SÉCURITÉ (FILET DE PROTECTION)
# ==================================================
@receiver(post_save, sender=Application)
def ensure_enrollment_after_acceptance(
    sender, instance: Application, created, **kwargs
):
    """
    FILET DE SÉCURITÉ INSTITUTIONNEL.

    ⚠️ CE SIGNAL N'EST PAS LE MOTEUR PRINCIPAL.
    ⚠️ IL EXISTE UNIQUEMENT POUR COUVRIR LES CAS OÙ :
       - quelqu’un modifie le status via l’admin Django
       - une migration ou un script bypass Application.accept()

    RÈGLE :
    - si la candidature est ACCEPTÉE
    - et qu'aucune inscription n'existe
    → on prépare l'inscription automatiquement

    ❌ aucune activation
    ❌ aucun matricule
    ❌ aucune logique financière avancée
    """

    # ❌ Ne rien faire à la création initiale
    if created:
        return

    # ❌ Ne s’intéresser QU’aux candidatures acceptées
    if instance.status != Application.STATUS_ACCEPTED:
        return

    # ❌ Si l’inscription existe déjà → STOP
    if hasattr(instance, "enrollment"):
        return

    # ✅ Préparation sécurisée (idempotente)
    try:
        prepare_enrollment(instance)
    except Exception:
        # ⚠️ ON NE CASSE JAMAIS L’ADMIN DJANGO
        # Les erreurs doivent être visibles en logs, pas bloquantes
        pass
