import openpyxl
from contacts.models import Contact
from emprunt.models import Emprunt
from equipements.models import Equipement
from django.db.models import Q
from emprunt.models import Emprunt

class EmpruntService:

    @staticmethod
    def importer_depuis_excel(fichier_excel):
        wb = openpyxl.load_workbook(fichier_excel)
        ws = wb.active
        erreurs = []
        succes = 0

        for num_ligne, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            email, object_dmd, date_empr, date_retour_prevu, etat, references = row

            try:
                beneficiaire = Contact.objects.get(email=email)
            except Contact.DoesNotExist:
                erreurs.append(f"Ligne {num_ligne} : aucun contact trouvé avec l'email '{email}'")
                continue

            emprunt = Emprunt.objects.create(
                beneficiaire=beneficiaire,
                object_dmd=object_dmd,
                date_empr=date_empr,
                date_retour_prevu=date_retour_prevu,
                etat=etat,
            )

            liste_references = [ref.strip() for ref in references.split(',')]
            for reference in liste_references:
                try:
                    equipement = Equipement.objects.get(reference=reference)
                    equipement.emprunt = emprunt
                    equipement.etat = 'emprunte'
                    equipement.save()
                except Equipement.DoesNotExist:
                    erreurs.append(f"Ligne {num_ligne} : équipement '{reference}' introuvable")

            succes += 1

        return succes, erreurs

    
    @staticmethod
    def liste_emprunts(query='', etat_filtre=''):
        emprunts = Emprunt.objects.all()

        if query:
            emprunts = emprunts.filter(
                Q(beneficiaire__nom__icontains=query) |
                Q(beneficiaire__prenom__icontains=query) |
                Q(beneficiaire__email__icontains=query) |
                Q(object_dmd__icontains=query)
            )

        if etat_filtre:
            emprunts = emprunts.filter(etat=etat_filtre)

        return emprunts

    @staticmethod
    def stats_emprunts():
        return {
            'total':     Emprunt.objects.count(),
            'en_cours':  Emprunt.objects.filter(etat='En cours').count(),
            'planifies': Emprunt.objects.filter(etat='Planifié').count(),
            'retournes': Emprunt.objects.filter(etat='Retourné').count(),
            'expires':   Emprunt.objects.filter(etat='Expiré').count(),
            'annules':   Emprunt.objects.filter(etat='Annulé').count(),
        }