# students/services/create_student.py

import secrets
import string

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from students.models import Student


User = get_user_model()


# ==================================================
# OUTILS
# ==================================================
def generate_password(length=10):
    """
    Génère un mot de passe sécurisé.
    """
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_matricule():
    """
    Exemple : ESFE-00023
    """
    last_student = Student.objects.order_by("-id").first()
    next_id = (last_student.id + 1) if last_student else 1
    return f"ESFE-{str(next_id).zfill(5)}"


# ==================================================
# SERVICE PRINCIPAL
# ==================================================
def create_student_after_first_payment(inscription):
    """
    Crée automatiquement :
    - le compte utilisateur
    - le profil étudiant
    UNIQUEMENT si aucun étudiant n’existe déjà
    pour cette inscription.

    Retourne :
    {
        "student": Student,
        "user": User,
        "password": str
    }
    ou None si déjà existant
    """

    # 🔒 Sécurité : ne jamais créer deux étudiants
    if hasattr(inscription, "student"):
        return None

    candidature = inscription.candidature

    with transaction.atomic():

        # ==========================
        # 1️⃣ CRÉATION USER
        # ==========================
        raw_password = generate_password()

        user = User.objects.create_user(
            username=candidature.email,
            email=candidature.email,
            password=raw_password,
            first_name=candidature.first_name,
            last_name=candidature.last_name,
            is_active=True,
        )

        # ==========================
        # 2️⃣ CRÉATION ÉTUDIANT
        # ==========================
        student = Student.objects.create(
            user=user,
            inscription=inscription,
            matricule=generate_matricule(),
            created_at=timezone.now(),
            is_active=True,
        )

        return {
            "student": student,
            "user": user,
            "password": raw_password,
        }
