from django import forms
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from .models import Gestionnaire
from django.conf import settings

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