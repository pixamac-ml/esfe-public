from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Candidature, CandidatureDocument


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
    # LISTE
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
    # LECTURE SEULE
    # ----------------------------------------------
    readonly_fields = (
        "submitted_at",
        "reviewed_at",
        "updated_at",
    )

    # ----------------------------------------------
    # STRUCTURE FORMULAIRE
    # ----------------------------------------------
    fieldsets = (
        ("Programme", {
            "fields": ("programme", "status")
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

    inlines = (CandidatureDocumentInline,)

    # ----------------------------------------------
    # ACTIONS
    # ----------------------------------------------
    actions = (
        "mark_under_review",
        "mark_accepted",
        "mark_accepted_with_reserve",
        "mark_to_complete",
        "mark_rejected",
    )

    # ==================================================
    # AFFICHAGES
    # ==================================================
    @admin.display(description="Candidat")
    def full_name(self, obj):
        return f"{obj.last_name} {obj.first_name}"

    @admin.display(description="Statut", ordering="status")
    def status_badge(self, obj):
        colors = {
            "submitted": "#6c757d",
            "under_review": "#0d6efd",
            "to_complete": "#ffc107",
            "accepted": "#198754",
            "accepted_with_reserve": "#20c997",
            "rejected": "#dc3545",
        }

        return format_html(
            '<span style="padding:4px 8px; border-radius:4px; '
            'background:{}; color:white; font-weight:600;">{}</span>',
            colors.get(obj.status, "#6c757d"),
            obj.get_status_display()
        )

    # ==================================================
    # ACTIONS MÉTIER (AVEC save() → SIGNAL OK)
    # ==================================================
    @admin.action(description="📂 En cours d’analyse")
    def mark_under_review(self, request, queryset):
        for candidature in queryset:
            candidature.status = "under_review"
            candidature.reviewed_at = timezone.now()
            candidature.save()

    @admin.action(description="✅ Accepter")
    def mark_accepted(self, request, queryset):
        for candidature in queryset:
            candidature.status = "accepted"
            candidature.reviewed_at = timezone.now()
            candidature.save()

    @admin.action(description="⚠️ Accepter sous réserve")
    def mark_accepted_with_reserve(self, request, queryset):
        for candidature in queryset:
            candidature.status = "accepted_with_reserve"
            candidature.reviewed_at = timezone.now()
            candidature.save()

    @admin.action(description="📝 Dossier à compléter")
    def mark_to_complete(self, request, queryset):
        for candidature in queryset:
            candidature.status = "to_complete"
            candidature.reviewed_at = timezone.now()
            candidature.save()

    @admin.action(description="❌ Refuser")
    def mark_rejected(self, request, queryset):
        for candidature in queryset:
            candidature.status = "rejected"
            candidature.reviewed_at = timezone.now()
            candidature.save()


# ==================================================
# ADMIN : DOCUMENTS DE CANDIDATURE
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

    readonly_fields = ("uploaded_at",)
