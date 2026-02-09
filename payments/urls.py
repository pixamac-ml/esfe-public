from django.urls import path
from .views import initiate_payment, receipt_public_detail, receipt_pdf

app_name = "payments"   # ← OBLIGATOIRE

urlpatterns = [
    path(
        "initiate/<uuid:reference>/",
        initiate_payment,
        name="initiate"
    ),

    path(
        "recu/<str:reference>/",
        receipt_public_detail,
        name="receipt_detail"
    ),

    path(
        "recu/<str:reference>/pdf/",
        receipt_pdf,
        name="receipt_pdf",
    ),
]
