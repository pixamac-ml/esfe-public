from formations.models import (
    Cycle,
    Diploma,
    Filiere,
    Programme,
    ProgrammeYear,
)

# -----------------------------
# CYCLES
# -----------------------------
cycles_data = [
    {
        "name": "Cycle Licence",
        "min": 3,
        "max": 3,
        "description": "Cycle supérieur – niveau Licence",
    },
    {
        "name": "Cycle Master",
        "min": 2,
        "max": 2,
        "description": "Cycle supérieur – niveau Master",
    },
]

cycles = {}
for c in cycles_data:
    cycle, _ = Cycle.objects.get_or_create(
        name=c["name"],
        defaults={
            "min_duration_years": c["min"],
            "max_duration_years": c["max"],
            "description": c["description"],
        }
    )
    cycles[c["name"]] = cycle


# -----------------------------
# DIPLOMES
# -----------------------------
diplomas_data = [
    ("Licence", "superieur"),
    ("Master", "superieur"),
    ("Diplôme d'État", "superieur"),
]

diplomas = {}
for name, level in diplomas_data:
    diploma, _ = Diploma.objects.get_or_create(
        name=name,
        defaults={"level": level}
    )
    diplomas[name] = diploma


# -----------------------------
# FILIERES
# -----------------------------
filieres_names = [
    "Infirmier d’État",
    "Sage-femme",
    "Technicien de laboratoire",
    "Biologie médicale",
    "Santé communautaire",
    "Nutrition",
    "Épidémiologie",
    "Hygiène Sécurité Travail",
    "Data Manager Santé",
]

filieres = {}
for name in filieres_names:
    filiere, _ = Filiere.objects.get_or_create(name=name)
    filieres[name] = filiere


# -----------------------------
# PROGRAMMES (FORMATIONS REELLES)
# -----------------------------
programmes_data = [
    {
        "title": "Infirmier d’État",
        "filiere": "Infirmier d’État",
        "cycle": "Cycle Licence",
        "diploma": "Diplôme d'État",
        "duration": 3,
        "short": "Formation complète et reconnue en soins infirmiers.",
        "desc": "La formation d’Infirmier d’État prépare les étudiants aux soins cliniques, à l’éthique professionnelle et à la prise en charge des patients.",
    },
    {
        "title": "Sage-femme",
        "filiere": "Sage-femme",
        "cycle": "Cycle Licence",
        "diploma": "Diplôme d'État",
        "duration": 3,
        "short": "Spécialisation en santé maternelle et néonatale.",
        "desc": "La formation de Sage-femme est orientée vers la santé de la mère et de l’enfant, avec une forte composante pratique.",
    },
    {
        "title": "Technicien de laboratoire",
        "filiere": "Technicien de laboratoire",
        "cycle": "Cycle Licence",
        "diploma": "Diplôme d'État",
        "duration": 2,
        "short": "Analyses biomédicales et diagnostics.",
        "desc": "Cette formation prépare aux techniques d’analyses médicales et au diagnostic biologique.",
    },
    {
        "title": "Santé communautaire",
        "filiere": "Santé communautaire",
        "cycle": "Cycle Master",
        "diploma": "Master",
        "duration": 2,
        "short": "Gestion et promotion de la santé publique.",
        "desc": "Le Master en Santé communautaire forme des cadres capables de concevoir et piloter des programmes de santé publique.",
    },
]

for p in programmes_data:
    programme, created = Programme.objects.get_or_create(
        title=p["title"],
        defaults={
            "filiere": filieres[p["filiere"]],
            "cycle": cycles[p["cycle"]],
            "diploma_awarded": diplomas[p["diploma"]],
            "duration_years": p["duration"],
            "short_description": p["short"],
            "description": p["desc"],
            "is_active": True,
            "is_featured": True,
        }
    )

    # Création automatique des années du programme
    if created:
        for year in range(1, p["duration"] + 1):
            ProgrammeYear.objects.get_or_create(
                programme=programme,
                year_number=year
            )

print("✔️ Données de formations créées avec succès.")
