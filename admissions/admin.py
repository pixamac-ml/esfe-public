from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import (
    Candidature,
    CandidatureDocument,
)

# ==================================================
# INLINE : DOCUMENTS DE LA CANDIDATURE
# ==================================================
class CandidatureDocumentInline(admin.TabularInline):
    model = CandidatureDocument
    extra = 0
    fields = (
        "document_type",
        "file",
        "is_valid",
        "admin_note",
        "uploaded_at",
    )
    readonly_fields = ("uploaded_at",)
    autocomplete_fields = ("document_type",)


# ==================================================
# ADMIN : CANDIDATURE
# ==================================================
@admin.register(Candidature)
class CandidatureAdmin(admin.ModelAdmin):

    # ----------------------------------------------
    # AFFICHAGE LISTE
    # ----------------------------------------------
    list_display = (
        "full_name",
        "programme",
        "status_badge",
        "phone",
        "email",
        "submitted_at",
        "reviewed_at",
    )

    list_filter = (
        "status",
        "programme__cycle",
        "programme__filiere",
        "programme",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone",
        "email",
        "programme__title",
    )

    ordering = ("-submitted_at",)
    list_per_page = 25

    # ----------------------------------------------
    # CHAMPS EN LECTURE SEULE
    # ----------------------------------------------
    readonly_fields = (
        "submitted_at",
        "reviewed_at",
        "updated_at",
    )

    # ----------------------------------------------
    # STRUCTURATION DU FORMULAIRE
    # ----------------------------------------------
    fieldsets = (
        ("Programme choisi", {
            "fields": (
                "programme",
                "status",
            )
        }),
        ("Informations personnelles", {
            "fields": (
                "first_name",
                "last_name",
                "gender",
                "birth_date",
                "birth_place",
            )
        }),
        ("Coordonnées", {
            "fields": (
                "phone",
                "email",
                "address",
                "city",
                "country",
            )
        }),
        ("Décision administrative", {
            "fields": (
                "admin_comment",
                "reviewed_at",
            )
        }),
        ("Système", {
            "fields": (
                "submitted_at",
                "updated_at",
            )
        }),
    )

    inlines = (
        CandidatureDocumentInline,
    )

    # ----------------------------------------------
    # ACTIONS ADMIN
    # ----------------------------------------------
    actions = (
        "mark_under_review",
        "mark_accepted",
        "mark_accepted_with_reserve",
        "mark_to_complete",
        "mark_rejected",
    )

    # ==================================================
    # MÉTHODES D’AFFICHAGE
    # ==================================================
    @admin.display(description="Candidat")
    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"

    @admin.display(description="Statut", ordering="status")
    def status_badge(self, obj):
        colors = {
            "submitted": "#6c757d",          # gris
            "under_review": "#0d6efd",       # bleu
            "to_complete": "#ffc107",        # orange
            "accepted": "#198754",           # vert
            "accepted_with_reserve": "#20c997",  # vert clair
            "rejected": "#dc3545",           # rouge
        }

        color = colors.get(obj.status, "#6c757d")

        return format_html(
            '<span style="padding:4px 8px; border-radius:4px; '
            'background-color:{}; color:white; font-weight:600;">{}</span>',
            color,
            obj.get_status_display()
        )

    # ==================================================
    # ACTIONS MÉTIER
    # ==================================================
    @admin.action(description="📂 Marquer comme : En cours d’analyse")
    def mark_under_review(self, request, queryset):
        queryset.update(
            status="under_review",
            reviewed_at=timezone.now()
        )

    @admin.action(description="✅ Accepter la candidature")
    def mark_accepted(self, request, queryset):
        queryset.update(
            status="accepted",
            reviewed_at=timezone.now()
        )

    @admin.action(description="⚠️ Accepter sous réserve")
    def mark_accepted_with_reserve(self, request, queryset):
        queryset.update(
            status="accepted_with_reserve",
            reviewed_at=timezone.now()
        )

    @admin.action(description="📝 Marquer : Dossier à compléter")
    def mark_to_complete(self, request, queryset):
        queryset.update(
            status="to_complete",
            reviewed_at=timezone.now()
        )

    @admin.action(description="❌ Refuser la candidature")
    def mark_rejected(self, request, queryset):
        queryset.update(
            status="rejected",
            reviewed_at=timezone.now()
        )


# ==================================================
# ADMIN : DOCUMENTS (ACCÈS DIRECT)
# ==================================================
@admin.register(CandidatureDocument)
class CandidatureDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "candidature",
        "document_type",
        "is_valid",
        "uploaded_at",
    )

    list_filter = (
        "is_valid",
        "document_type",
    )

    search_fields = (
        "candidature__first_name",
        "candidature__last_name",
        "document_type__name",
    )

    ordering = ("-uploaded_at",)
    list_per_page = 25

    readonly_fields = (
        "uploaded_at",
    )
