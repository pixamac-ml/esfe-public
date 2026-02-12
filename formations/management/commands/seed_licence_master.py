from django.core.management.base import BaseCommand
from formations.models import (
    Cycle, Diploma, Filiere,
    Programme, ProgrammeYear,
    Fee, RequiredDocument,
    ProgrammeRequiredDocument
)


class Command(BaseCommand):
    help = "Seed Licence (3 ans) et Master (2 ans) pour ESFE"

    def handle(self, *args, **kwargs):

        # =============================
        # CYCLES
        # =============================

        licence, _ = Cycle.objects.get_or_create(
            name="Licence",
            defaults={
                "description": "Cycle supérieur professionnel – Bac +3",
                "min_duration_years": 3,
                "max_duration_years": 3,
                "is_active": True
            }
        )

        master, _ = Cycle.objects.get_or_create(
            name="Master",
            defaults={
                "description": "Cycle supérieur spécialisé – Bac +5",
                "min_duration_years": 2,
                "max_duration_years": 2,
                "is_active": True
            }
        )

        # =============================
        # DIPLOMES
        # =============================

        diplome_licence, _ = Diploma.objects.get_or_create(
            name="Licence Professionnelle en Sciences de la Santé",
            level="superieur"
        )

        diplome_master, _ = Diploma.objects.get_or_create(
            name="Master en Sciences de la Santé",
            level="superieur"
        )

        # =============================
        # FILIERE UNIQUE
        # =============================

        filiere, _ = Filiere.objects.get_or_create(
            name="Sciences de la Santé",
            defaults={
                "description": "Formations professionnelles et universitaires en santé",
                "is_active": True
            }
        )

        # =============================
        # DOCUMENTS REQUIS
        # =============================

        documents = [
            "Demande timbrée",
            "Copie extrait de naissance",
            "Copie légalisée du diplôme requis",
            "Certificat de fréquentation",
            "Quatre photos d'identité"
        ]

        document_instances = []
        for doc in documents:
            d, _ = RequiredDocument.objects.get_or_create(
                name=doc,
                defaults={"is_mandatory": True}
            )
            document_instances.append(d)

        # =====================================================
        # FONCTION CREATION PROGRAMME COMPLET
        # =====================================================

        def create_programme(
            title,
            cycle,
            diploma,
            duration,
            yearly_amount,
            description_extra=""
        ):

            programme, created = Programme.objects.get_or_create(
                title=title,
                defaults={
                    "filiere": filiere,
                    "cycle": cycle,
                    "diploma_awarded": diploma,
                    "duration_years": duration,
                    "short_description": f"Formation professionnelle en {title}",
                    "description": f"""
OBJECTIFS :
Former des professionnels compétents en {title} capables d'intervenir efficacement dans le système de santé.

COMPÉTENCES ACQUISES :
- Maîtrise des pratiques professionnelles en {title}
- Gestion des situations cliniques
- Travail en équipe pluridisciplinaire
- Application des normes éthiques et sanitaires

DÉBOUCHÉS :
- Hôpitaux publics et privés
- Centres de santé communautaires
- ONG et structures internationales
- Cliniques spécialisées

ADMISSION :
Accès sur étude de dossier académique.

{description_extra}
""",
                    "is_active": True,
                    "is_featured": True
                }
            )

            # Années
            for year in range(1, duration + 1):
                py, _ = ProgrammeYear.objects.get_or_create(
                    programme=programme,
                    year_number=year
                )

                Fee.objects.get_or_create(
                    programme_year=py,
                    label="Frais annuels",
                    defaults={
                        "amount": yearly_amount,
                        "due_month": "Janvier"
                    }
                )

            # Documents requis attachés à chaque programme
            for doc in document_instances:
                ProgrammeRequiredDocument.objects.get_or_create(
                    programme=programme,
                    document=doc
                )

            self.stdout.write(self.style.SUCCESS(f"{title} ✔ créé"))

        # =====================================================
        # LICENCE (3 ANS)
        # =====================================================

        licence_programmes = [
            "Infirmier d'État",
            "Sage-Femme",
            "Biologie Médicale"
        ]

        for prog in licence_programmes:
            create_programme(
                title=prog,
                cycle=licence,
                diploma=diplome_licence,
                duration=3,
                yearly_amount=410000
            )

        # =====================================================
        # MASTER (2 ANS)
        # =====================================================

        master_programmes = [
            "Biologie Médicale",
            "Gynécologie Obstétrique",
            "Médecine d'Urgence",
            "Odontologie",
            "Management en Santé",
            "Biochimie",
            "Pédagogie en Santé",
            "Pédiatrie",
            "Néphrologie",
            "Cardiologie",
            "Dermatologie",
            "Anesthésie Réanimation",
            "Puériculture",
            "Kinésithérapie",
            "Soins Infirmiers",
            "Épidémiologie",
            "Suivi et Évaluation",
            "Santé Sexuelle et Reproduction",
            "Science Alimentaire Nutrition",
            "Économie de la Santé",
            "Santé Communautaire",
            "Santé Environnementale"
        ]

        for prog in master_programmes:
            create_programme(
                title=prog,
                cycle=master,
                diploma=diplome_master,
                duration=2,
                yearly_amount=410000
            )

        self.stdout.write(self.style.SUCCESS("LICENCE & MASTER SEED TERMINÉ 🚀"))
