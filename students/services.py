import secrets
from django.contrib.auth.models import User
from students.models import Student


def create_student_after_first_payment(inscription):
    """
    Crée le compte étudiant UNE SEULE FOIS
    après le premier paiement validé.
    """

    # 🔒 Sécurité absolue
    if hasattr(inscription, "student"):
        return None  # étudiant déjà créé

    candidature = inscription.candidature

    # Identifiants
    username = f"etu_{inscription.id}"
    password = secrets.token_urlsafe(8)

    user = User.objects.create_user(
        username=username,
        email=candidature.email,
        password=password,
        first_name=candidature.first_name,
        last_name=candidature.last_name,
    )

    student = Student.objects.create(
        user=user,
        inscription=inscription,
        matricule=f"ESFE-{inscription.id:05d}"
    )

    return {
        "student": student,
        "password": password,  # À utiliser plus tard pour l’email
    }
