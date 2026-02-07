from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from .models import Application
from inscriptions.models import Enrollment, AcademicYear
from payments.models import FeeTemplate, Fee


# ==================================================
# OUTIL MÉTIER
# ==================================================
def get_active_academic_year():
    """
    Retourne l'année académique active.
    Il doit y en avoir UNE et une seule.
    """
    return AcademicYear.objects.filter(is_active=True).first()


# ==================================================
# SIGNAL : ACCEPTATION D’UNE CANDIDATURE
# ==================================================
@receiver(post_save, sender=Application)
def prepare_enrollment_after_acceptance(
    sender, instance: Application, created, **kwargs
):
    """
    AUTOMATISME INSTITUTIONNEL (PRÉPARATOIRE)

    Lorsqu'une candidature passe au statut ACCEPTÉ :
    - créer l'inscription administrative (PENDING)
    - rattacher à l'année académique active
    - générer les frais à payer

    ⚠️ AUCUNE activation ici
    ⚠️ AUCUN matricule ici
    ⚠️ AUCUNE décision académique automatique
    """

    # ❌ Ne rien faire à la création initiale
    if created:
        return

    # ❌ Ne déclencher QUE si le statut est ACCEPTÉ
    if instance.status != Application.STATUS_ACCEPTED:
        return

    # ❌ Sécurité : éviter toute duplication
    if hasattr(instance, "enrollment"):
        return

    academic_year = get_active_academic_year()

    # ❌ Sécurité métier : pas d'année académique active
    if not academic_year:
        # On ne casse PAS l’admin ici
        return

    with transaction.atomic():

        # 1️⃣ Création de l'inscription administrative (PRÉPARATION)
        enrollment = Enrollment.objects.create(
            application=instance,
            academic_year=academic_year,
            status=Enrollment.STATUS_PENDING,
            is_active=False,  # 🔐 accès plateforme BLOQUÉ
        )

        # 2️⃣ Génération des frais à partir des templates
        fee_templates = FeeTemplate.objects.filter(
            programme=instance.programme,
            is_active=True
        ).order_by("order")

        for template in fee_templates:
            Fee.objects.create(
                enrollment=enrollment,
                template=template,
                amount_expected=template.amount
            )
