from django import forms
from django.forms import formset_factory

from .models import Candidate, Application


# --------------------------------------------------
# FORMULAIRE CANDIDAT
# --------------------------------------------------
class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "birth_place",
            "phone",
            "email",
            "address",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }


# --------------------------------------------------
# FORMULAIRE CANDIDATURE
# --------------------------------------------------
class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["motivation"]
        widgets = {
            "motivation": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Expliquez brièvement votre motivation…"
            }),
        }


# --------------------------------------------------
# FORMULAIRE SIMPLE POUR UN DOCUMENT
# --------------------------------------------------
class RequiredDocumentUploadForm(forms.Form):
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput()
    )


# --------------------------------------------------
# FORMSET DOCUMENTS (SANS MODELE)
# --------------------------------------------------
RequiredDocumentFormSet = formset_factory(
    RequiredDocumentUploadForm,
    extra=0
)
