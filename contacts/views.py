from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
import openpyxl

from .models import Contact
from .forms import ContactForm, ImportExcelContactForm


@login_required
def liste_contacts(request):
    """Affiche la liste des contacts (emprunteurs) avec recherche."""
    query = request.GET.get('q', '')
    type_filtre = request.GET.get('type', '')

    contacts = Contact.objects.filter(est_actif=True)

    if query:
        contacts = contacts.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(matricule__icontains=query)
        )
    if type_filtre:
        contacts = contacts.filter(type_contact=type_filtre)

    stats = {
        'total': Contact.objects.filter(est_actif=True).count(),
        'etudiants': Contact.objects.filter(type_contact='etudiant', est_actif=True).count(),
        'enseignants': Contact.objects.filter(type_contact='enseignant', est_actif=True).count(),
        'autres': Contact.objects.filter(est_actif=True).exclude(type_contact__in=['etudiant', 'enseignant']).count(),
    }

    context = {
        'contacts': contacts,
        'query': query,
        'type_filtre': type_filtre,
        'stats': stats,
        'types': Contact.TYPE_CHOICES,
    }
    return render(request, 'contacts/liste.html', context)


@login_required
def detail_contact(request, pk):
    """Affiche la fiche détaillée d'un contact."""
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, 'contacts/detail.html', {'contact': contact})


@login_required
def creer_contact(request):
    """Crée un nouveau contact."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f"Le contact « {contact.nom_complet} » a été créé avec succès.")
            return redirect('liste_contacts')
        else:
            messages.error(request, "Erreur lors de la création. Vérifiez les champs.")
    else:
        form = ContactForm()
    return render(request, 'contacts/form.html', {'form': form, 'action': 'Créer', 'titre': 'Ajouter un contact'})


@login_required
def modifier_contact(request, pk):
    """Modifie un contact existant."""
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le contact « {contact.nom_complet} » a été modifié.")
            return redirect('detail_contact', pk=pk)
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/form.html', {'form': form, 'action': 'Modifier', 'titre': 'Modifier le contact', 'contact': contact})


@login_required
def retirer_contact(request, pk):
    """Retire (désactive) un contact."""
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        contact.est_actif = False
        contact.save()
        messages.success(request, f"Le contact « {contact.nom_complet} » a été retiré.")
        return redirect('liste_contacts')
    return render(request, 'contacts/confirmer_suppression.html', {'objet': contact, 'type': 'contact'})


@login_required
def importer_contacts(request):
    """Importe des contacts depuis un fichier Excel."""
    if request.method == 'POST':
        form = ImportExcelContactForm(request.POST, request.FILES)
        if form.is_valid():
            fichier = request.FILES['fichier_excel']
            try:
                wb = openpyxl.load_workbook(fichier)
                ws = wb.active
                nb_crees = 0
                nb_erreurs = 0
                erreurs = []

                for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    if not any(row):
                        continue
                    try:
                        nom = str(row[0]).strip() if row[0] else ''
                        prenom = str(row[1]).strip() if row[1] else ''
                        email = str(row[2]).strip() if row[2] else ''
                        telephone = str(row[3]).strip() if row[3] else ''
                        type_contact = str(row[4]).strip().lower() if row[4] else 'etudiant'
                        matricule = str(row[5]).strip() if row[5] else ''
                        filiere = str(row[6]).strip() if row[6] else ''

                        if not nom or not email:
                            erreurs.append(f"Ligne {i}: nom ou email manquant")
                            nb_erreurs += 1
                            continue

                        types_valides = ['etudiant', 'enseignant', 'personnel', 'externe']
                        if type_contact not in types_valides:
                            type_contact = 'etudiant'

                        if Contact.objects.filter(email=email).exists():
                            erreurs.append(f"Ligne {i}: email « {email} » déjà existant, ignoré")
                            nb_erreurs += 1
                            continue

                        Contact.objects.create(
                            nom=nom,
                            prenom=prenom,
                            email=email,
                            telephone=telephone,
                            type_contact=type_contact,
                            matricule=matricule,
                            filiere=filiere,
                        )
                        nb_crees += 1
                    except Exception as e:
                        erreurs.append(f"Ligne {i}: {str(e)}")
                        nb_erreurs += 1

                msg = f"{nb_crees} contact(s) importé(s) avec succès."
                if nb_erreurs:
                    msg += f" {nb_erreurs} ligne(s) ignorée(s)."
                messages.success(request, msg)
                for err in erreurs[:5]:
                    messages.warning(request, err)
                return redirect('liste_contacts')

            except Exception as e:
                messages.error(request, f"Erreur lors de la lecture du fichier : {str(e)}")
        else:
            messages.error(request, "Fichier invalide.")
    else:
        form = ImportExcelContactForm()
    return render(request, 'contacts/importer.html', {'form': form})
