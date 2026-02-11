from django.utils import timezone
from datetime import timedelta
import random

from payments.models import PaymentAgent, CashPaymentSession


# ============================================================
# 1️⃣ Vérifier agent + créer (ou récupérer) session active
# ============================================================

def verify_agent_and_create_session(inscription, agent_full_name):
    """
    Vérifie que l’agent existe.
    Réutilise une session active si elle existe.
    Sinon crée une nouvelle session (valide 5 minutes).
    """

    if not agent_full_name:
        return None, None, "Nom de l’agent requis."

    agent_full_name = agent_full_name.strip()

    if len(agent_full_name) < 2:
        return None, None, "Nom invalide."

    # 🔎 Recherche par prénom ET nom (plus fiable)
    name_parts = agent_full_name.split()

    queryset = PaymentAgent.objects.select_related("user").filter(
        is_active=True
    )

    for part in name_parts:
        queryset = queryset.filter(
            user__first_name__icontains=part
        ) | queryset.filter(
            user__last_name__icontains=part
        )

    agent = queryset.distinct().first()

    if not agent:
        return None, None, "Agent introuvable."

    # 🧹 Nettoyage des sessions expirées
    CashPaymentSession.objects.filter(
        inscription=inscription,
        agent=agent,
        expires_at__lt=timezone.now()
    ).update(is_used=True)

    # 🔁 Recherche session active valide
    session = CashPaymentSession.objects.filter(
        inscription=inscription,
        agent=agent,
        is_used=False,
        expires_at__gt=timezone.now()
    ).order_by("-created_at").first()

    # ➕ Si aucune session valide → en créer une
    if not session:
        session = CashPaymentSession.objects.create(
            inscription=inscription,
            agent=agent,
            verification_code=str(random.randint(100000, 999999)),
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False
        )

    return agent, session, None


# ============================================================
# 2️⃣ Validation code dynamique
# ============================================================

def validate_cash_code(inscription, agent, code):
    """
    Vérifie que :
    - une session active existe
    - le code correspond
    - il n’est pas expiré
    Marque la session comme utilisée si OK.
    """

    if not code:
        return False, "Code requis."

    session = CashPaymentSession.objects.filter(
        inscription=inscription,
        agent=agent,
        is_used=False
    ).order_by("-created_at").first()

    if not session:
        return False, "Aucune session active trouvée."

    if timezone.now() > session.expires_at:
        session.is_used = True
        session.save(update_fields=["is_used"])
        return False, "Code expiré."

    if session.verification_code != code:
        return False, "Code invalide."

    # ✅ Marquer comme utilisé
    session.is_used = True
    session.save(update_fields=["is_used"])

    return True, None
