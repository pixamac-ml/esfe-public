from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone

from .models import Payment
from students.models import StudentProfile


# =================================================
# SIGNAL PRINCIPAL : VALIDATION DE PAIEMENT
# =================================================

@receiver(post_save, sender=Payment)
def handle_validated_payment(sender, instance: Payment, created, **kwargs):
    """
    AUTOMATISME FINANCIER CENTRAL (CŒUR DU SYSTÈME) :

    Paiement VALIDÉ →
    - recalcul du frais
    - si tous les frais obligatoires sont réglés :
        → activation de l'inscription
        → création du profil étudiant
    """

    # ❌ On ignore tout ce qui n'est pas un paiement validé
    if instance.status != Payment.STATUS_VALIDATED:
        return

    fee = instance.fee
    enrollment = fee.enrollment

    with transaction.atomic():

        # 1️⃣ Recalculer l'état du frais
        fee_is_settled = fee.recalculate_status()

        # Si le frais n'est pas encore soldé → on s'arrête
        if not fee_is_settled:
            return

        # 2️⃣ Vérifier si TOUS les frais obligatoires sont soldés
        mandatory_fees = enrollment.fees.filter(
            template__is_mandatory=True
        )

        if not mandatory_fees.exists():
            return

        if not all(f.is_settled for f in mandatory_fees):
            return

        # 3️⃣ Activer l'inscription (AUTOMATIQUE, IDÉMPOTENT)
        if not enrollment.is_active:
            enrollment.is_active = True
            enrollment.finalized_at = timezone.now()
            enrollment.save(update_fields=["is_active", "finalized_at"])

        # 4️⃣ Créer le profil étudiant (UNE SEULE FOIS)
        StudentProfile.objects.get_or_create(
            enrollment=enrollment,
            defaults={
                "is_active": True,
                "activated_at": timezone.now(),
            }
        )

        # ⚠️ RÈGLES D’OR :
        # - on NE TOUCHE PAS enrollment.status ici
        # - aucune décision académique automatique
        # - tout est piloté par l’argent, pas par l’admin
