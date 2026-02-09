from django.urls import path
from .views import initiate_payment

app_name = "payments"   # ← OBLIGATOIRE

urlpatterns = [
    path(
        "initiate/<uuid:reference>/",
        initiate_payment,
        name="initiate"
    ),
]
