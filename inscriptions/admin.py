from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import AcademicYear, Enrollment


# ==================================================
# ANNÉE ACADÉMIQUE
# ==================================================
@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = ("is_active",)
    search_fields = ("label",)
    ordering = ("-start_date",)

    actions = ["set_as_active_year"]

    @admin.action(description="Définir comme année académique active")
    def set_as_active_year(self, request, queryset):
        AcademicYear.objects.update(is_active=False)
        queryset.update(is_active=True)


# ==================================================
# INSCRIPTION ADMINISTRATIVE
# ==================================================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "matricule",
        "get_candidate",
        "get_programme",
        "academic_year",
        "status",
        "is_active",
        "enrolled_at",
        "finalize_link",
    )

    list_filter = (
        "status",
        "academic_year",
        "is_active",
    )

    search_fields = (
        "matricule",
        "application__candidate__first_name",
        "application__candidate__last_name",
        "application__candidate__email",
        "application__programme__title",
    )

    # 🔒 Champs techniques non modifiables
    readonly_fields = (
        "matricule",
        "is_active",
        "enrolled_at",
        "validated_at",
        "validated_by",
        "public_token",
        "finalize_link",
        "finalized_at",
    )

    fieldsets = (
        ("Informations générales", {
            "fields": (
                "application",
                "academic_year",
                "status",
            )
        }),
        ("Accès candidat (lien public)", {
            "fields": (
                "public_token",
                "finalize_link",
            )
        }),
        ("Validation administrative", {
            "fields": (
                "validated_at",
                "validated_by",
            )
        }),
        ("Notes internes", {
            "fields": ("notes",)
        }),
        ("État système (lecture seule)", {
            "fields": (
                "is_active",
                "matricule",
                "finalized_at",
                "enrolled_at",
            )
        }),
    )

    actions = [
        "validate_enrollment_admin",
        "suspend_enrollment",
        "cancel_enrollment",
    ]

    # ==================================================
    # ACTIONS ADMIN (HUMAINES UNIQUEMENT)
    # ==================================================
    @admin.action(description="Valider administrativement l'inscription")
    def validate_enrollment_admin(self, request, queryset):
        for enrollment in queryset:
            enrollment.validate_admin(user=request.user)

    @admin.action(description="Suspendre l'inscription")
    def suspend_enrollment(self, request, queryset):
        for enrollment in queryset:
            enrollment.suspend(reason="Suspendu par l'administration")

    @admin.action(description="Annuler l'inscription")
    def cancel_enrollment(self, request, queryset):
        for enrollment in queryset:
            enrollment.cancel()

    # ==================================================
    # MÉTHODES D’AFFICHAGE
    # ==================================================
    @admin.display(description="Candidat")
    def get_candidate(self, obj):
        return obj.application.candidate

    @admin.display(description="Formation")
    def get_programme(self, obj):
        return obj.application.programme.title

    @admin.display(description="Lien de finalisation")
    def finalize_link(self, obj):
        url = reverse(
            "inscriptions:finalize_enrollment",
            args=[obj.public_token]
        )
        return format_html(
            '<a href="{}" target="_blank">Ouvrir le lien</a>',
            url
        )
