from django.contrib import admin, messages
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

    # ==================================================
    # PROTECTION CRITIQUE : ACCEPTATION VIA FORMULAIRE
    # ==================================================
    def save_model(self, request, obj, form, change):
        """
        Empêche toute acceptation silencieuse via le formulaire admin.
        Toute acceptation DOIT passer par Application.accept()
        """
        if change and "status" in form.changed_data:
            if obj.status == Application.STATUS_ACCEPTED:
                obj.accept()
                self.message_user(
                    request,
                    "Candidature acceptée et inscription préparée automatiquement.",
                    messages.SUCCESS
                )
                return

        super().save_model(request, obj, form, change)

    # ==================================================
    # ACTIONS ACADÉMIQUES (MÉTIER UNIQUEMENT)
    # ==================================================
    @admin.action(description="Marquer comme en étude")
    def mark_under_review(self, request, queryset):
        for application in queryset:
            application.mark_under_review()

        self.message_user(
            request,
            "Candidature(s) marquée(s) comme en étude.",
            messages.INFO
        )

    @admin.action(description="Marquer comme dossier incomplet")
    def mark_incomplete(self, request, queryset):
        for application in queryset:
            application.mark_incomplete()

        self.message_user(
            request,
            "Candidature(s) marquée(s) comme incomplète(s).",
            messages.WARNING
        )

    @admin.action(description="Accepter les candidatures")
    def accept_applications(self, request, queryset):
        count = 0
        for application in queryset:
            application.accept()
            count += 1

        self.message_user(
            request,
            f"{count} candidature(s) acceptée(s) — inscription(s) préparée(s) automatiquement.",
            messages.SUCCESS
        )

    @admin.action(description="Refuser les candidatures")
    def reject_applications(self, request, queryset):
        for application in queryset:
            application.reject()

        self.message_user(
            request,
            "Candidature(s) refusée(s).",
            messages.ERROR
        )
