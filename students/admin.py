from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "matricule",
        "full_name",
        "programme",
        "is_active",
        "created_at",
    )

    search_fields = (
        "matricule",
        "user__username",
        "inscription__candidature__first_name",
        "inscription__candidature__last_name",
    )

    list_filter = (
        "is_active",
        "inscription__candidature__programme",
    )

    def full_name(self, obj):
        c = obj.inscription.candidature
        return f"{c.last_name} {c.first_name}"

    def programme(self, obj):
        return obj.inscription.candidature.programme.title
