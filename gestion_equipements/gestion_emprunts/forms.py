from django import forms
from .models import Emprunt


class EmpruntModificationForm(forms.ModelForm):
    """
    RG.04 — Modification restreinte : uniquement date_emprunt et beneficiaire.
    Les équipements liés NE PEUVENT PAS être modifiés via ce formulaire.
    """

    class Meta:
        model  = Emprunt
        fields = ['date_emprunt', 'beneficiaire']  # ← SEULEMENT CES 2 CHAMPS
        widgets = {
            'date_emprunt': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'beneficiaire': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'date_emprunt': "Date d'emprunt",
            'beneficiaire': "Bénéficiaire",
        }

    def clean(self):
        cleaned_data = super().clean()
        emprunt = self.instance
        # Bloquer si l'emprunt est dans un état terminal
        if emprunt.pk and emprunt.statut in ('RETOURNE', 'ANNULE', 'EXPIRE'):
            raise forms.ValidationError(
                f"Un emprunt '{emprunt.get_statut_display()}' ne peut plus être modifié."
            )
        return cleaned_data
