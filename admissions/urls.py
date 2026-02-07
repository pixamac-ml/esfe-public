from django.http import HttpResponse
from django.urls import path
from . import views

app_name = "admissions"

urlpatterns = [
    path(
        "candidature/<slug:programme_slug>/",
        views.start_application,
        name="start_application"
    ),
    path(
        "succes/",
        views.application_success,
        name="application_success"
    ),
    path("test/", lambda r: HttpResponse("ADMISSIONS OK")),

]
