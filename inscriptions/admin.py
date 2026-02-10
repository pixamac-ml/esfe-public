from django.contrib import admin
from .models import Inscription
from django.contrib import admin
from django.utils.html import format_html

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "reference",
        "candidature",
        "status",
        "created_at",
        "public_link",
        "amount_due",
        "amount_paid",
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
        "public_token",
    )


    @admin.display(description="Lien public")
    def public_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">🔗 Ouvrir le dossier</a>',
            obj.get_public_url()
        )
