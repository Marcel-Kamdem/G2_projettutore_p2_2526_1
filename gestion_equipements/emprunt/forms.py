from django import forms

class ImportEmpruntForm(forms.Form):
    fichier_excel = forms.FileField(
        label="Fichier Excel",
        widget=forms.FileInput(attrs={'accept': '.xlsx,.xls'})
    )