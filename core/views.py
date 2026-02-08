# core/views.py
from django.shortcuts import render

def home(request):
    pillars = [
        {
            "title": "Sciences de la santé",
            "description": "Formations spécialisées.",
        },
        {
            "title": "Encadrement académique",
            "description": "Corps enseignant qualifié.",
        },
        {
            "title": "Exigence académique",
            "description": "Rigueur et suivi.",
        },
        {
            "title": "Ouverture",
            "description": "Étudiants nationaux et internationaux.",
        },
    ]

    return render(request, "home.html", {
        "pillars": pillars,
    })
