# students/services/email.py

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_student_credentials_email(*, student, raw_password):
    """
    Envoi l’email de bienvenue à l’étudiant
    après création automatique du compte.
    """

    user = student.user
    inscription = student.inscription

    subject = "🎓 Bienvenue à l’ESFE – Accès à votre espace étudiant"

    context = {
        "student": student,
        "user": user,
        "password": raw_password,
        "public_link": inscription.get_public_url(),
        "login_url": settings.STUDENT_LOGIN_URL,
    }

    message = render_to_string(
        "emails/student_welcome.txt",
        context
    )

    html_message = render_to_string(
        "emails/student_welcome.html",
        context
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
