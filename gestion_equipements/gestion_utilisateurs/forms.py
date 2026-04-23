from django import forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import Gestionnaire
from django.conf import settings
from django.contrib.auth import password_validation


class ModifierMotDePasseForm(forms.Form):
    ancien_mdp = forms.CharField(
        label="Mot de passe actuel",
        widget=forms.PasswordInput(attrs={'class': 'form-Field', 'placeholder': 'Mot de passe actuel'})
    )
    nouveau_mdp = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-Field', 'placeholder': 'Nouveau mot de passe'}),
        help_text=password_validation.password_validators_help_text_html()
    )
    confirmation_mdp = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-Field', 'placeholder': 'Confirmer le mot de passe'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_ancien_mdp(self):
        ancien = self.cleaned_data.get('ancien_mdp')
        if not self.user.check_password(ancien):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")
        return ancien

    def clean(self):
        cleaned = super().clean()
        nouveau = cleaned.get('nouveau_mdp')
        confirmation = cleaned.get('confirmation_mdp')
        if nouveau and confirmation and nouveau != confirmation:
            self.add_error('confirmation_mdp', "Les deux mots de passe ne correspondent pas.")
        if nouveau:
            password_validation.validate_password(nouveau, self.user)
        return cleaned

    def save(self):
        nouveau = self.cleaned_data['nouveau_mdp']
        self.user.set_password(nouveau)
        self.user.save()
        return self.user

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class':'form-Field',
        'placeholder':'Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class':'form-Field',
        'placeholder':'Password'
    }))


class GestionnaireCreationForm(forms.ModelForm):
    email = forms.EmailField (required=True ,widget=forms.TextInput(attrs={
        'class':'form-Field',
        'placeholder':'Email'
    }))
    last_name = forms.CharField(required=True ,widget=forms.TextInput(attrs={
        'class':'form-Field',
        'placeholder':'Last Name'
    }))
    first_name = forms.CharField(required=True ,widget=forms.TextInput(attrs={
        'class':'form-Field',
        'placeholder':'First Name'
    }))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class':'form-Field',
        'placeholder':'UserName'
    }))

    class Meta:
        model = Gestionnaire
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = get_random_string(length=8)
        user.set_password(password)
        user.is_staff = False
        user.role = 'Gestionnaire'
        print("___Gestionnaire cree___")
        print(f"Username : {user.username}")
        print(f"first name : {user.first_name}")
        print(f"last name : {user.last_name}")
        print(f" email : {user.email}")
        print(f" password : {password}")
        if commit:
            user.save()
            sujet = "Vos identifiants de connexion"
            message = f"Bonjour {user.last_name} {user.first_name}, \n\n Votre compte a été créé \nIdentifiant : {user.username}\nMot de passe : {password}"
            destinataire = [user.email]

            send_mail(sujet, message, settings.EMAIL_HOST_USER,destinataire)
        return user