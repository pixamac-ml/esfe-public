# inscriptions/views.py
from django.shortcuts import render, get_object_or_404
from .models import Inscription


def inscription_public_detail(request, reference):
    """
    Vue publique d’une inscription.
    Accessible via un lien unique (UUID).
    """

    inscription = get_object_or_404(
        Inscription,
        reference=reference
    )

    context = {
        "inscription": inscription,
        "candidature": inscription.candidature,
        "programme": inscription.candidature.programme,
    }

    return render(
        request,
        "inscriptions/public_detail.html",
        context
    )
