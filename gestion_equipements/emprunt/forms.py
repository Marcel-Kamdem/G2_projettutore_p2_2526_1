from django import forms
from .models import Emprunt


class ModifierEmpruntForm(forms.ModelForm):
    """
    RG.04 – Modification limitée.
    Seuls 2 champs sont autorisés : date_empr et beneficiaire.
    Les équipements, l'objet de la demande, etc. sont BLOQUÉS.
    """

    class Meta:
        model  = Emprunt
        fields = ['date_empr', 'beneficiaire']   # ← SEULEMENT ces 2 champs
        widgets = {
            'date_empr': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-input',
                }
            ),
            'beneficiaire': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
        }
        labels = {
            'date_empr'    : "Date d'emprunt",
            'beneficiaire' : "Bénéficiaire",
        }
