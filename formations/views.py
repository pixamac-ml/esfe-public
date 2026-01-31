from django.shortcuts import render

from django.urls import reverse

def formation_list(request):
    formations = [
        {
            "title": "Infirmier d’État",
            "description": "Formation complète et reconnue.",
            "duration": "3 ans",
            "slug": "infirmier-etat",
        },
        {
            "title": "Sage-femme",
            "description": "Spécialisation en santé maternelle.",
            "duration": "3 ans",
            "slug": "sage-femme",
        },
        {
            "title": "Technicien de laboratoire",
            "description": "Analyses biomédicales et diagnostics.",
            "duration": "2 ans",
            "slug": "technicien-labo",
        },
    ]

    for f in formations:
        f["url"] = reverse("formations:detail", kwargs={"slug": f["slug"]})



    return render(request, "formations/list.html", {
        "formations": formations
    })




def formation_detail(request, slug):
    formation = {
        "title": "Infirmier d’État",
        "description": (
            "La formation d’Infirmier d’État prépare les étudiants aux "
            "exigences professionnelles du secteur de la santé."
        ),
        "duration": "3 ans",
        "objectives": [
            "Acquérir les compétences cliniques fondamentales",
            "Maîtriser les soins infirmiers",
            "Développer l’éthique professionnelle",
        ],
    }

    return render(request, "formations/detail.html", {
        "formation": formation
    })
