# payments/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment, Receipt


@receiver(post_save, sender=Payment)
def create_receipt_on_validation(sender, instance, created, **kwargs):
    """
    Crée automatiquement un reçu quand un paiement est validé.
    """

    if instance.status != "validated":
        return

    # Sécurité : pas de doublon
    if hasattr(instance, "receipt"):
        return

    Receipt.objects.create(
        payment=instance,
        issued_by="Administration ESFE"
    )


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from payments.models import Payment
from students.models import Student
from students.services.matricule import generate_matricule


@receiver(post_save, sender=Payment)
def create_student_on_first_payment(sender, instance, **kwargs):
    """
    Crée automatiquement l’étudiant après le premier paiement validé.
    """

    if instance.status != "validated":
        return

    inscription = instance.inscription

    # 🔒 Sécurité : déjà étudiant
    if hasattr(inscription, "student"):
        return

    candidature = inscription.candidature

    # 1️⃣ Création du compte utilisateur
    username = f"{candidature.first_name.lower()}.{candidature.last_name.lower()}"
    email = candidature.email

    user = User.objects.create_user(
        username=username,
        email=email
    )

    # 2️⃣ Création de l’étudiant
    student = Student.objects.create(
        user=user,
        inscription=inscription
    )

    # 3️⃣ Génération du matricule
    student.matricule = generate_matricule(student)
    student.save(update_fields=["matricule"])
