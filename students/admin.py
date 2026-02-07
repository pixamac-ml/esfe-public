from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "get_matricule",
        "get_candidate",
        "is_active",
        "activated_at",
    )

    list_filter = ("is_active",)
    search_fields = (
        "enrollment__matricule",
        "enrollment__application__candidate__last_name",
        "enrollment__application__candidate__first_name",
    )

    readonly_fields = ("activated_at", "created_at")

    def has_add_permission(self, request):
        return False  # 🔐 création automatique uniquement

    @admin.display(description="Matricule")
    def get_matricule(self, obj):
        return obj.enrollment.matricule

    @admin.display(description="Étudiant")
    def get_candidate(self, obj):
        return obj.enrollment.application.candidate
