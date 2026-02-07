from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods

from formations.models import Programme
from .models import Candidate, Application, ApplicationDocument
from .forms import (
    CandidateForm,
    ApplicationForm,
    RequiredDocumentFormSet,
)


# --------------------------------------------------
# PAGE DE CANDIDATURE (PUBLIQUE)
# --------------------------------------------------
@require_http_methods(["GET", "POST"])
def start_application(request, programme_slug):
    programme = get_object_or_404(
        Programme.objects.prefetch_related("required_documents__document"),
        slug=programme_slug,
        is_active=True
    )

    required_documents = [
        rd.document for rd in programme.required_documents.all()
    ]

    if request.method == "POST":
        candidate_form = CandidateForm(request.POST)
        application_form = ApplicationForm(request.POST)
        document_formset = RequiredDocumentFormSet(
            request.POST,
            request.FILES
        )

        if (
            candidate_form.is_valid()
            and application_form.is_valid()
            and document_formset.is_valid()
        ):
            email = candidate_form.cleaned_data["email"]

            # 🔒 Vérifier si le candidat existe déjà
            candidate, _ = Candidate.objects.get_or_create(
                email=email,
                defaults=candidate_form.cleaned_data
            )

            # 🔒 Empêcher double candidature pour la même formation
            if Application.objects.filter(
                candidate=candidate,
                programme=programme
            ).exists():
                messages.warning(
                    request,
                    "Vous avez déjà soumis une candidature pour cette formation."
                )
                return redirect("admissions:application_success")

            with transaction.atomic():

                # 1️⃣ Création de la candidature
                application = application_form.save(commit=False)
                application.candidate = candidate
                application.programme = programme
                application.save()

                # 2️⃣ Enregistrement des documents requis
                uploaded_documents = 0

                for form, document in zip(
                    document_formset.forms,
                    required_documents
                ):
                    uploaded_file = form.cleaned_data.get("file")
                    if uploaded_file:
                        ApplicationDocument.objects.create(
                            application=application,
                            document=document,
                            file=uploaded_file
                        )
                        uploaded_documents += 1

                # 🔒 Vérification finale des documents requis
                if uploaded_documents < len(required_documents):
                    messages.warning(
                        request,
                        "Votre dossier a été soumis mais certains documents sont manquants."
                    )

            # 🔐 Marqueur de succès (session)
            request.session["application_success"] = {
                "programme_title": programme.title,
                "candidate_name": f"{candidate.first_name} {candidate.last_name}",
            }

            return redirect("admissions:application_success")

        messages.error(
            request,
            "Veuillez corriger les erreurs du formulaire."
        )

    else:
        candidate_form = CandidateForm()
        application_form = ApplicationForm()
        document_formset = RequiredDocumentFormSet(
            initial=[{} for _ in required_documents]
        )

    documents_with_forms = list(zip(
        document_formset.forms,
        required_documents
    ))

    context = {
        "programme": programme,
        "candidate_form": candidate_form,
        "application_form": application_form,
        "document_formset": document_formset,
        "documents_with_forms": documents_with_forms,
        "required_documents": required_documents,
    }

    return render(
        request,
        "admissions/application_form.html",
        context
    )


# --------------------------------------------------
# PAGE DE CONFIRMATION
# --------------------------------------------------
@require_http_methods(["GET"])
def application_success(request):
    data = request.session.get("application_success")

    if not data:
        return redirect("formations:list")

    request.session.pop("application_success", None)

    return render(
        request,
        "admissions/application_success.html",
        {
            "programme_title": data["programme_title"],
            "candidate_name": data["candidate_name"],
        }
    )
