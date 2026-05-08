from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'email', 'telephone', 'type_contact', 'matricule', 'filiere', 'adresse', 'notes']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-Field', 'placeholder': 'Email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Téléphone'}),
            'type_contact': forms.Select(attrs={'class': 'form-Field'}),
            'matricule': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Matricule / Identifiant'}),
            'filiere': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Filière / Département'}),
            'adresse': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Adresse...', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Notes supplémentaires...', 'rows': 2}),
        }


class ImportExcelContactForm(forms.Form):
    fichier_excel = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-Field', 'accept': '.xlsx,.xls'}),
        label="Fichier Excel (.xlsx ou .xls)"
    )
