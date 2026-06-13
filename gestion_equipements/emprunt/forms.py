from django import forms
from .models import Mouvement


class ImportMouvementForm(forms.Form):
    fichier_excel = forms.FileField(
        label="Fichier Excel",
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )


class MouvementForm(forms.ModelForm):
    """Formulaire de création d'un mouvement (entrée, emprunt, sortie)."""

    class Meta:
        model = Mouvement
        fields = [
            'type_operation',
            'equipement',
            'date_operation',
            'gestionnaire',
            'notes',
            # emprunt
            'beneficiaire',
            'objet_demande',
            'date_retour_prevu',
            'date_retour_effectif',
            'etat',
            # sortie
            'destination',
        ]
        widgets = {
            'date_operation': forms.DateInput(attrs={'type': 'date'}),
            'date_retour_prevu': forms.DateInput(attrs={'type': 'date'}),
            'date_retour_effectif': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'message_admin': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Exclure les équipements déjà en emprunt actif
        ids_occupes = Mouvement.objects.filter(
            type_operation='emprunt',
            etat__in=["EN_COURS", "PLANIFIE", "VALIDE"]
        ).values_list('equipement_id', flat=True)

        # Si modification, ne pas exclure l'équipement courant
        if self.instance and self.instance.pk and self.instance.equipement_id:
            ids_occupes = [i for i in ids_occupes if i != self.instance.equipement_id]

        EquipementModel = self.fields['equipement'].queryset.model
        self.fields['equipement'].queryset = EquipementModel.objects.filter(
            est_actif=True
        ).exclude(id__in=ids_occupes)

        # Champs non obligatoires par défaut (gérés via clean() du modèle)
        self.fields['beneficiaire'].required = False
        self.fields['objet_demande'].required = False
        self.fields['date_retour_prevu'].required = False
        self.fields['destination'].required = False
        self.fields['gestionnaire'].required = False

    def clean(self):
        cleaned_data = super().clean()
        type_op = cleaned_data.get('type_operation')
        beneficiaire = cleaned_data.get('beneficiaire')
        destination = cleaned_data.get('destination')
        date_retour = cleaned_data.get('date_retour_prevu')

        if type_op == 'emprunt':
            if not beneficiaire:
                self.add_error('beneficiaire', "Un bénéficiaire est obligatoire pour un emprunt.")
            if not date_retour:
                self.add_error('date_retour_prevu', "La date de retour prévue est obligatoire pour un emprunt.")

        if type_op == 'sortie':
            if not destination:
                self.add_error('destination', "La destination est obligatoire pour une sortie.")

        return cleaned_data


class MouvementModificationForm(forms.ModelForm):
    """Formulaire de modification d'un mouvement existant (emprunt)."""

    class Meta:
        model = Mouvement
        fields = [
            'beneficiaire',
            'date_operation',
            'date_retour_prevu',
            'date_retour_effectif',
            'etat',
            'equipement',
            'objet_demande',
            'message_admin',
        ]
        widgets = {
            'date_operation': forms.DateInput(attrs={'type': 'date'}),
            'date_retour_prevu': forms.DateInput(attrs={'type': 'date'}),
            'date_retour_effectif': forms.DateInput(attrs={'type': 'date'}),
            'message_admin': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipement'].disabled = True
        self.fields['objet_demande'].disabled = True