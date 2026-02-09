# inscriptions/urls.py
from django.urls import path
from .views import inscription_public_detail

app_name = "inscriptions"

urlpatterns = [
    path(
        "i/<uuid:reference>/",
        inscription_public_detail,
        name="public_detail"
    ),
]
