from django.urls import path
from . import views

app_name = "inscriptions"

urlpatterns = [
    path(
        "finaliser-inscription/<uuid:token>/",
        views.finalize_enrollment,
        name="finalize_enrollment"
    ),
]
