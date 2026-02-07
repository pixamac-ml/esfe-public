from django.contrib import admin
from .models import Candidate, Application, ApplicationDocument


# ==================================================
# CANDIDAT
# ==================================================
@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "phone",
        "email",
        "created_at",
    )

    search_fields = (
        "last_name",
        "first_name",
        "phone",
        "email",
    )

    ordering = ("last_name",)
    list_per_page = 25


# ==================================================
# DOCUMENTS DE CANDIDATURE (INLINE)
# ==================================================
class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0

    fields = (
        "document",
        "file",
        "is_valid",
        "uploaded_at",
    )

    readonly_fields = (
        "uploaded_at",
    )


# ==================================================
# CANDIDATURE (DOSSIER ACADÉMIQUE)
# ==================================================
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "candidate",
        "programme",
        "status",
        "submitted_at",
        "reviewed_at",
    )

    list_filter = (
        "status",
        "programme",
    )

    search_fields = (
        "candidate__last_name",
        "candidate__first_name",
        "candidate__email",
        "programme__title",
    )

    ordering = ("-submitted_at",)

    inlines = (ApplicationDocumentInline,)

    actions = (
        "mark_under_review",
        "mark_incomplete",
        "accept_applications",
        "reject_applications",
    )

    # -------------------------
    # ACTIONS ACADÉMIQUES
    # -------------------------
    @admin.action(description="Marquer comme en étude")
    def mark_under_review(self, request, queryset):
        for application in queryset:
            application.mark_under_review()

    @admin.action(description="Marquer comme dossier incomplet")
    def mark_incomplete(self, request, queryset):
        queryset.update(status=Application.STATUS_INCOMPLETE)

    @admin.action(description="Accepter les candidatures")
    def accept_applications(self, request, queryset):
        for application in queryset:
            application.accept()

    @admin.action(description="Refuser les candidatures")
    def reject_applications(self, request, queryset):
        for application in queryset:
            application.reject()
