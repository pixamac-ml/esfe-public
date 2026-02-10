# inscriptions/admin.py

from django.contrib import admin, messages
from django.db import transaction
from django.utils.html import format_html

from .models import Inscription
from inscriptions.services import create_inscription_from_candidature
from admissions.models import Candidature


# ==================================================
# ACTION ADMIN : ACCEPTER CANDIDATURE
# ==================================================
@admin.action(description="✅ Accepter la candidature et créer l’inscription")
def accepter_candidature(modeladmin, request, queryset):
    """
    Action institutionnelle :
    - accepte officiellement une candidature
    - crée UNE inscription (si absente)
    - copie le prix du programme dans amount_due
    """

    created_count = 0
    skipped_count = 0

    for candidature in queryset:

        # 🔒 Déjà acceptée
        if candidature.status in ("accepted", "accepted_with_reserve"):
            skipped_count += 1
            continue

        # 🔒 Inscription déjà existante
        if hasattr(candidature, "inscription"):
            skipped_count += 1
            continue

        programme = candidature.programme
        amount_due = programme.total_price

        with transaction.atomic():
            create_inscription_from_candidature(
                candidature=candidature,
                amount_due=amount_due
            )

            candidature.status = "accepted"
            candidature.save(update_fields=["status"])

        created_count += 1

    if created_count:
        modeladmin.message_user(
            request,
            f"{created_count} inscription(s) créée(s) avec succès.",
            level=messages.SUCCESS
        )

    if skipped_count:
        modeladmin.message_user(
            request,
            f"{skipped_count} candidature(s) ignorée(s) "
            f"(déjà acceptée ou inscription existante).",
            level=messages.WARNING
        )


# ==================================================
# ADMIN INSCRIPTION
# ==================================================
@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    """
    Administration des inscriptions.

    RÈGLES :
    - amount_due est modifiable (cas particuliers)
    - amount_paid est STRICTEMENT en lecture seule
    - AUCUNE logique financière ici
    """

    # ==================================================
    # LISTE
    # ==================================================
    list_display = (
        "id",
        "reference",
        "candidate_name",
        "programme_title",
        "status_badge",
        "amount_due_display",
        "amount_paid_display",
        "balance_display",
        "created_at",
        "public_link",
    )

    list_filter = ("status",)
    ordering = ("-created_at",)
    list_per_page = 25

    search_fields = (
        "reference",
        "candidature__first_name",
        "candidature__last_name",
        "candidature__programme__title",
    )

    # ==================================================
    # CHAMPS
    # ==================================================
    readonly_fields = (
        "reference",
        "public_token",
        "amount_paid",
        "created_at",
    )

    fieldsets = (
        ("Candidature", {
            "fields": (
                "candidature",
            )
        }),
        ("Statut", {
            "fields": (
                "status",
            )
        }),
        ("Finances (copie figée)", {
            "description": (
                "Le montant à payer est copié depuis le programme "
                "au moment de l’acceptation. "
                "Il peut être ajusté ici en cas particulier "
                "(bourse, remise, correction)."
            ),
            "fields": (
                "amount_due",
                "amount_paid",
            )
        }),
        ("Système", {
            "fields": (
                "reference",
                "public_token",
                "created_at",
            )
        }),
    )

    actions = [accepter_candidature]

    # ==================================================
    # MÉTHODES D’AFFICHAGE
    # ==================================================
    @admin.display(description="Candidat")
    def candidate_name(self, obj):
        c = obj.candidature
        return f"{c.last_name} {c.first_name}"

    @admin.display(description="Formation")
    def programme_title(self, obj):
        return obj.candidature.programme.title

    @admin.display(description="Statut")
    def status_badge(self, obj):
        colors = {
            "created": "#0d6efd",
            "active": "#198754",
            "suspended": "#dc3545",
        }
        return format_html(
            '<span style="padding:4px 8px; border-radius:4px; '
            'background:{}; color:white; font-weight:600;">{}</span>',
            colors.get(obj.status, "#6c757d"),
            obj.get_status_display()
        )

    @admin.display(description="Total")
    def amount_due_display(self, obj):
        return format_html("<strong>{} FCFA</strong>", obj.amount_due)

    @admin.display(description="Payé")
    def amount_paid_display(self, obj):
        return format_html("{} FCFA", obj.amount_paid)

    @admin.display(description="Solde")
    def balance_display(self, obj):
        return format_html(
            "<strong>{} FCFA</strong>",
            obj.balance
        )

    @admin.display(description="Lien public étudiant")
    def public_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="font-weight:600;">'
            '🔗 Ouvrir le dossier</a>',
            obj.get_public_url()
        )
