from django import forms
from .models import Contact
from salles.models import Salle


class ContactForm(forms.ModelForm):
    salle = forms.ModelChoiceField(
        queryset=Salle.objects.filter(est_active=True),
        required=False,
        label="Salle de classe",
        widget=forms.Select(attrs={'class': 'form-Field'}),
        empty_label="— Sélectionner une salle —"
    )

    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'email', 'telephone', 'type_contact',
                  'matricule', 'filiere', 'adresse', 'notes']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-Field', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Téléphone'}),
            'type_contact': forms.Select(attrs={'class': 'form-Field', 'id': 'id_type_contact'}),
            'matricule': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Matricule / Identifiant'}),
            'filiere': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Filière / Département'}),
            'adresse': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Adresse...', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Notes supplémentaires...', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pré-remplir la salle si le contact existe déjà
        if self.instance and self.instance.pk and self.instance.salle:
            self.fields['salle'].initial = self.instance.salle

    def clean(self):
        cleaned_data = super().clean()
        type_contact = cleaned_data.get('type_contact')
        salle = cleaned_data.get('salle')
        if type_contact == 'etudiant' and not salle:
            self.add_error('salle', "La salle est obligatoire pour un étudiant.")
        return cleaned_data

    def save(self, commit=True):
        contact = super().save(commit=False)
        salle = self.cleaned_data.get('salle')
        contact.salle = salle  # sera None pour non-étudiants
        if commit:
            contact.save()
        return contact


class ImportExcelContactForm(forms.Form):
    fichier_excel = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-Field', 'accept': '.xlsx,.xls'}),
        label="Fichier Excel (.xlsx ou .xls)"
    )