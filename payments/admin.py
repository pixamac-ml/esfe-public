# payments/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html

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

    readonly_fields = (
        "requested_at",
        "validated_at",
    )

    fieldsets = (
        ("Inscription", {
            "fields": ("inscription",)
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

    # ----------------------------------------------
    # ACTIONS ADMIN
    # ----------------------------------------------
    actions = ("validate_payments",)

    @admin.action(description="✅ Valider le paiement sélectionné")
    def validate_payments(self, request, queryset):
        """
        Action admin :
        - valide les paiements en attente
        - met à jour l'inscription associée
        """

        validated_count = 0

        for payment in queryset:
            if payment.status != "pending":
                continue

            payment.validate()
            validated_count += 1

            # 🔹 Activation automatique si solde réglé
            inscription = payment.inscription
            if inscription.balance == 0 and inscription.status != "active":
                inscription.status = "active"
                inscription.save(update_fields=["status"])

        if validated_count:
            self.message_user(
                request,
                f"{validated_count} paiement(s) validé(s) avec succès.",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "Aucun paiement en attente à valider.",
                level=messages.WARNING
            )

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


from django.contrib import admin
from .models import Receipt


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "candidate",
        "programme",
        "amount",
        "issued_at",
    )

    search_fields = (
        "reference",
        "payment__inscription__candidature__first_name",
        "payment__inscription__candidature__last_name",
    )

    readonly_fields = (
        "reference",
        "issued_at",
        "payment",
    )

    def candidate(self, obj):
        c = obj.payment.inscription.candidature
        return f"{c.last_name} {c.first_name}"

    def programme(self, obj):
        return obj.payment.inscription.candidature.programme.title

    def amount(self, obj):
        return f"{obj.payment.amount} FCFA"


@admin.display(description="Reçu")
def receipt_link(self, obj):
    if obj.receipt_pdf:
        return format_html(
            '<a href="{}" target="_blank">📄 Télécharger</a>',
            obj.receipt_pdf.url
        )
    return "-"
