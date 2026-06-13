import openpyxl
from contacts.models import Contact
from equipements.models import Equipement
from django.db.models import Q
from .models import Mouvement


class MouvementService:

    @staticmethod
    def importer_depuis_excel(fichier_excel):
        """
        Importe des mouvements de type 'entree' depuis un fichier Excel.
        Colonnes attendues : nom_equipement, reference, date_operation, notes
        """
        wb = openpyxl.load_workbook(fichier_excel)
        ws = wb.active
        erreurs = []
        succes = 0

        for num_ligne, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):
                continue
            try:
                nom_equipement = str(row[0]).strip() if row[0] else ''
                reference = str(row[1]).strip() if row[1] else ''
                date_operation = row[2]
                notes = str(row[3]).strip() if row[3] else ''

                if not nom_equipement:
                    erreurs.append(f"Ligne {num_ligne} : nom d'équipement manquant")
                    continue

                # Récupérer ou créer l'équipement
                if reference:
                    equipement, cree = Equipement.objects.get_or_create(
                        reference=reference,
                        defaults={'nom': nom_equipement, 'est_actif': True}
                    )
                else:
                    equipement = Equipement.objects.filter(nom=nom_equipement).first()
                    if not equipement:
                        erreurs.append(f"Ligne {num_ligne} : équipement '{nom_equipement}' introuvable (pas de référence)")
                        continue

                Mouvement.objects.create(
                    equipement=equipement,
                    type_operation='entree',
                    date_operation=date_operation,
                    notes=notes,
                )
                succes += 1

            except Exception as e:
                erreurs.append(f"Ligne {num_ligne} : {str(e)}")

        return succes, erreurs

    @staticmethod
    def liste_mouvements(query='', type_filtre='', etat_filtre=''):
        mouvements = Mouvement.objects.select_related(
            'equipement', 'beneficiaire', 'gestionnaire'
        )

        if query:
            mouvements = mouvements.filter(
                Q(equipement__nom__icontains=query) |
                Q(beneficiaire__nom__icontains=query) |
                Q(beneficiaire__prenom__icontains=query) |
                Q(beneficiaire__email__icontains=query) |
                Q(objet_demande__icontains=query)
            )

        if type_filtre:
            mouvements = mouvements.filter(type_operation=type_filtre)

        if etat_filtre:
            mouvements = mouvements.filter(etat=etat_filtre)

        return mouvements

    @staticmethod
    def stats_mouvements():
        return {
            'total': Mouvement.objects.count(),
            'entrees': Mouvement.objects.filter(type_operation='entree').count(),
            'emprunts': Mouvement.objects.filter(type_operation='emprunt').count(),
            'sorties': Mouvement.objects.filter(type_operation='sortie').count(),
            'en_cours': Mouvement.objects.filter(type_operation='emprunt', etat='EN_COURS').count(),
            'planifies': Mouvement.objects.filter(type_operation='emprunt', etat='PLANIFIE').count(),
            'retournes': Mouvement.objects.filter(type_operation='emprunt', etat='RETOURNE').count(),
            'expires': Mouvement.objects.filter(type_operation='emprunt', etat='EXPIRE').count(),
        }