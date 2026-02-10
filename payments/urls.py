# payments/urls.py

from django.urls import path
from . import views
from .views import student_initiate_payment
from .views import student_initiate_payment, receipt_pdf
app_name = "payments"

urlpatterns = [
    path(
        "initiate/<uuid:reference>/",
        views.initiate_payment,
        name="initiate"
    ),
    path(
        "initier/<str:token>/",
        views.student_initiate_payment,
        name="student_initiate",  # 👈 C’EST CE NOM QUI COMPTE
    ),

    path(
        "receipt/<str:receipt_number>/pdf/",
        views.receipt_pdf,
        name="receipt_pdf",
    ),
    path(
        "initier/<str:token>/",
        student_initiate_payment,
        name="initiate"
    ),

    path(
        "initier/<str:token>/",
        student_initiate_payment,
        name="initiate"
    ),
    path(
        "receipt/<str:receipt_number>/pdf/",
        receipt_pdf,
        name="receipt_pdf"
    ),
]


