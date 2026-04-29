from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from emprunt.models import Emprunt
from emprunt.emprunt_service import EmpruntService
from emprunt.forms import ImportEmpruntForm

def importer_emprunts_view(request):
    form = ImportEmpruntForm()
    contexte = {'form': form}

    if request.method == 'POST':
        form = ImportEmpruntForm(request.POST, request.FILES)

        if form.is_valid():
            fichier = request.FILES['fichier_excel']
            succes, erreurs = EmpruntService.importer_depuis_excel(fichier)

            # On passe les résultats au template
            contexte['form']    = form
            contexte['succes']  = succes
            contexte['erreurs'] = erreurs

    return render(request, 'emprunt/importer.html', contexte)


@login_required
def liste_emprunts(request):
    query       = request.GET.get('q', '')
    etat_filtre = request.GET.get('etat', '')

    emprunts = EmpruntService.liste_emprunts(query, etat_filtre)
    stats    = EmpruntService.stats_emprunts()

    context = {
        'emprunts':    emprunts,
        'query':       query,
        'etat_filtre': etat_filtre,
        'stats':       stats,
        'etats':       Emprunt.EMPRUNT_STATE,
    }
    return render(request, 'emprunt/liste.html', context)