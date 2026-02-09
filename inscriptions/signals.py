from django.db.models.signals import post_save
from django.dispatch import receiver

from admissions.models import Candidature
from .models import Inscription


@receiver(post_save, sender=Candidature)
def create_inscription_on_accept(sender, instance, created, **kwargs):
    print("🔥 SIGNAL post_save(Candidature) DÉCLENCHÉ")

    if created:
        print("➡️ Création initiale ignorée")
        return

    print(f"➡️ Statut actuel : {instance.status}")

    if instance.status in ("accepted", "accepted_with_reserve"):
        if hasattr(instance, "inscription"):
            print("⛔ Inscription déjà existante")
            return

        Inscription.objects.create(
            candidature=instance,
            status="created"
        )
        print("✅ INSCRIPTION CRÉÉE")
