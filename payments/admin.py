from django.contrib import admin
from django.utils import timezone

from .models import FeeTemplate, Fee, Payment


# ==================================================
# RÈGLES DE FRAIS (CONFIGURATION INSTITUTIONNELLE)
# ==================================================
@admin.register(FeeTemplate)
class FeeTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "programme",
        "label",
        "fee_type",
        "amount",
        "order",
        "is_mandatory",
        "is_active",
    )

    list_filter = (
        "programme",
        "fee_type",
        "is_mandatory",
        "is_active",
    )

    search_fields = (
        "label",
        "programme__title",
    )

    ordering = ("programme", "order")

    list_editable = (
        "order",
        "is_active",
    )

    readonly_fields = ()

    list_per_page = 25


# ==================================================
# FRAIS CONCRETS (PAR INSCRIPTION)
# ==================================================
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = (
        "get_matricule",
        "get_candidate",
        "template",
        "amount_expected",
        "amount_override",
        "total_paid",
        "remaining_amount",
        "is_settled",
        "created_at",
    )

    list_filter = (
        "is_settled",
        "template__fee_type",
        "template__programme",
    )

    search_fields = (
        "enrollment__matricule",
        "enrollment__application__candidate__first_name",
        "enrollment__application__candidate__last_name",
        "template__label",
    )

    readonly_fields = (
        "created_at",
        "total_paid",
        "remaining_amount",
    )

    autocomplete_fields = (
        "enrollment",
        "template",
    )

    fieldsets = (
        ("Lien académique", {
            "fields": (
                "enrollment",
                "template",
            )
        }),
        ("Montants", {
            "fields": (
                "amount_expected",
                "amount_override",
            )
        }),
        ("État du frais", {
            "fields": (
                "total_paid",
                "remaining_amount",
                "is_settled",
            )
        }),
        ("Traçabilité", {
            "fields": ("created_at",)
        }),
    )

    list_per_page = 25

    # -------------------------
    # AFFICHAGE
    # -------------------------
    @admin.display(description="Matricule")
    def get_matricule(self, obj):
        return obj.enrollment.matricule

    @admin.display(description="Étudiant")
    def get_candidate(self, obj):
        return obj.enrollment.application.candidate


# ==================================================
# PAIEMENTS (OPÉRATIONNEL)
# ==================================================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "get_matricule",
        "get_candidate",
        "amount_paid",
        "method",
        "status",
        "paid_at",
        "validated_by",
        "created_at",
    )

    list_filter = (
        "status",
        "method",
        "fee__template__fee_type",
    )

    search_fields = (
        "fee__enrollment__matricule",
        "fee__enrollment__application__candidate__first_name",
        "fee__enrollment__application__candidate__last_name",
        "reference",
    )

    readonly_fields = (
        "paid_at",
        "validated_by",
        "created_at",
    )

    autocomplete_fields = (
        "fee",
    )

    fieldsets = (
        ("Paiement", {
            "fields": (
                "fee",
                "amount_paid",
                "method",
                "reference",
            )
        }),
        ("Statut", {
            "fields": (
                "status",
                "paid_at",
                "validated_by",
            )
        }),
        ("Traçabilité", {
            "fields": ("created_at",)
        }),
    )

    actions = (
        "validate_payments",
        "reject_payments",
    )

    list_per_page = 25

    # -------------------------
    # ACTIONS ADMIN (HUMAINES)
    # -------------------------
    @admin.action(description="Valider les paiements sélectionnés")
    def validate_payments(self, request, queryset):
        for payment in queryset:
            if payment.status == Payment.STATUS_PENDING:
                payment.validate(user=request.user)

    @admin.action(description="Rejeter les paiements sélectionnés")
    def reject_payments(self, request, queryset):
        queryset.update(status=Payment.STATUS_REJECTED)

    # -------------------------
    # AFFICHAGE
    # -------------------------
    @admin.display(description="Matricule")
    def get_matricule(self, obj):
        return obj.fee.enrollment.matricule

    @admin.display(description="Étudiant")
    def get_candidate(self, obj):
        return obj.fee.enrollment.application.candidate
