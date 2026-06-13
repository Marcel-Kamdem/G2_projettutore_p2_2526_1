from django import forms
from .models import Inventaire, LigneInventaire


class InventaireForm(forms.ModelForm):
    class Meta:
        model = Inventaire
        fields = ['date_debut', 'date_fin', 'description']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class LigneInventaireForm(forms.ModelForm):
    class Meta:
        model = LigneInventaire
        fields = ['statut', 'quantite_constatee', 'observations']
        widgets = {
            'observations': forms.Textarea(attrs={'rows': 2}),
        }