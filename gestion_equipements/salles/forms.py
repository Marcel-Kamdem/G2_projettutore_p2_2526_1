# salles/forms.py
from django import forms
from .models import Salle

class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['nom', 'type_salle', 'description', 'capacite']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }