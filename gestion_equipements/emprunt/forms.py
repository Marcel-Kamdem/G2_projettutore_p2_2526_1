from django import forms
from .models import Emprunt

class ImportEmpruntForm(forms.Form):
    fichier_excel = forms.FileField(
        label="Fichier Excel",
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )

class EmpruntForm(forms.ModelForm):
    class Meta:
        model = Emprunt
        fields = [
            'equipement',
            'beneficiaire',
            'object_dmd',
            'date_retour_prevu',
            'date_retour_effect',
            'etat'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        EquipementModel = self.fields['equipement'].queryset.model
        
        ids_occupes = Emprunt.objects.filter(
            etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
        ).values_list('equipement_id', flat=True)

        if self.instance and self.instance.pk and hasattr(self.instance, 'equipement') and self.instance.equipement:
            ids_occupes = [id for id in ids_occupes if id != self.instance.equipement_id]

        self.fields['equipement'].queryset = EquipementModel.objects.exclude(
            id__in=ids_occupes
        ).distinct()
