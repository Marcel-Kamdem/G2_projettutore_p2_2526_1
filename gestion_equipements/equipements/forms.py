from django import forms
from .models import Equipement, Categorie


class EquipementForm(forms.ModelForm):
    class Meta:
        model = Equipement
        fields = ['nom', 'reference', 'categorie', 'description', 'etat', 'localisation', 'date_acquisition', 'image', 'notes']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Nom de l\'équipement'}),
            'reference': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Référence (ex: EQ-001)'}),
            'categorie': forms.Select(attrs={'class': 'form-Field'}),
            'description': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Description...', 'rows': 3}),
            'etat': forms.Select(attrs={'class': 'form-Field'}),
            'localisation': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Salle, bâtiment...'}),
            'date_acquisition': forms.DateInput(attrs={'class': 'form-Field', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Notes supplémentaires...', 'rows': 2}),
        }


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-Field', 'placeholder': 'Nom de la catégorie'}),
            'description': forms.Textarea(attrs={'class': 'form-Field', 'placeholder': 'Description...', 'rows': 3}),
        }


class ImportExcelForm(forms.Form):
    fichier_excel = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-Field', 'accept': '.xlsx,.xls'}),
        label="Fichier Excel (.xlsx ou .xls)"
    )
