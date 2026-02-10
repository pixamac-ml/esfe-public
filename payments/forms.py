# payments/forms.py

from django import forms
from payments.models import Payment


class StudentPaymentForm(forms.Form):
    """
    Formulaire utilisé par l'étudiant
    pour INITIER une demande de paiement.
    """

    METHOD_CHOICES = Payment.METHOD_CHOICES

    method = forms.ChoiceField(
        choices=METHOD_CHOICES,
        label="Méthode de paiement",
        widget=forms.Select(
            attrs={
                "class": "w-full border border-gray-300 rounded-lg px-4 py-2"
            }
        )
    )

    amount = forms.IntegerField(
        min_value=1,
        label="Montant à payer (FCFA)",
        widget=forms.NumberInput(
            attrs={
                "class": "w-full border border-gray-300 rounded-lg px-4 py-2",
                "placeholder": "Ex : 50000"
            }
        )
    )
