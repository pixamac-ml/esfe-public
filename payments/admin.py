# payments/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Administration des paiements.
    Validation MANUELLE par l’administration (Option B).
    """

    # ----------------------------------------------
    # LISTE
    # ----------------------------------------------
    list_display = (
        "id",
        "inscription_reference",
        "candidate_name",
        "programme",
        "amount_display",
        "method_badge",
        "status_badge",
        "requested_at",
        "validated_at",
    )

    list_filter = (
        "method",
        "status",
        "requested_at",
        "validated_at",
    )

    search_fields = (
        "reference",
        "inscription__reference",
        "inscription__candidature__first_name",
        "inscription__candidature__last_name",
        "inscription__candidature__programme__title",
    )

    ordering = ("-requested_at",)
    list_per_page = 25

    # ----------------------------------------------
    # CHAMPS EN LECTURE SEULE
    # ----------------------------------------------
    readonly_fields = (
        "requested_at",
        "validated_at",
    )

    # ----------------------------------------------
    # STRUCTURE DU FORMULAIRE
    # ----------------------------------------------
    fieldsets = (
        ("Inscription", {
            "fields": (
                "inscription",
            )
        }),
        ("Paiement", {
            "fields": (
                "amount",
                "method",
                "status",
                "reference",
            )
        }),
        ("Traçabilité", {
            "fields": (
                "requested_at",
                "validated_at",
            )
        }),
    )

    autocomplete_fields = ("inscription",)

    # ==================================================
    # MÉTHODES D’AFFICHAGE
    # ==================================================
    @admin.display(description="Référence inscription")
    def inscription_reference(self, obj):
        return obj.inscription.reference

    @admin.display(description="Candidat")
    def candidate_name(self, obj):
        c = obj.inscription.candidature
        return f"{c.last_name} {c.first_name}"

    @admin.display(description="Formation")
    def programme(self, obj):
        return obj.inscription.candidature.programme.title

    @admin.display(description="Montant")
    def amount_display(self, obj):
        return format_html("<strong>{} FCFA</strong>", obj.amount)

    @admin.display(description="Méthode")
    def method_badge(self, obj):
        colors = {
            "cash": "#6c757d",
            "orange_money": "#fd7e14",
            "bank_transfer": "#0d6efd",
        }
        return format_html(
            '<span style="padding:4px 8px; border-radius:4px; '
            'background:{}; color:white; font-weight:600;">{}</span>',
            colors.get(obj.method, "#6c757d"),
            obj.get_method_display()
        )

    @admin.display(description="Statut")
    def status_badge(self, obj):
        colors = {
            "pending": "#ffc107",
            "validated": "#198754",
            "cancelled": "#dc3545",
        }
        return format_html(
            '<span style="padding:4px 8px; border-radius:4px; '
            'background:{}; color:white; font-weight:600;">{}</span>',
            colors.get(obj.status, "#6c757d"),
            obj.get_status_display()
        )
