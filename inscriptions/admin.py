from django.contrib import admin
from .models import Inscription


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "candidature",
        "status",
        "created_at",
    )

    list_filter = ("status",)

    search_fields = (
        "reference",
        "candidature__first_name",
        "candidature__last_name",
        "candidature__programme__title",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "reference",
        "created_at",
    )
