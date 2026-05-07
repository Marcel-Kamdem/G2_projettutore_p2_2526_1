# Migration Sprint 3 - Fonctionnalités : modification limitée + validation admin
# Auteur : [Ton nom] – branche feature/modification-validation-emprunt

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emprunt', '0002_emprunt_etat'),
    ]

    operations = [
        # Rendre date_empr modifiable (supprimer auto_now_add)
        migrations.AlterField(
            model_name='emprunt',
            name='date_empr',
            field=models.DateField(verbose_name="Date d'emprunt"),
        ),
        # Agrandir le champ object_dmd
        migrations.AlterField(
            model_name='emprunt',
            name='object_dmd',
            field=models.CharField(max_length=200, verbose_name='Objet de la demande'),
        ),
        # Ajouter le champ type_emprunt
        migrations.AddField(
            model_name='emprunt',
            name='type_emprunt',
            field=models.CharField(
                choices=[('simple', 'Emprunt simple'), ('planifie', 'Emprunt planifié')],
                default='planifie',
                max_length=20,
                verbose_name='Type',
            ),
        ),
        # Mettre à jour les états disponibles
        migrations.AlterField(
            model_name='emprunt',
            name='etat',
            field=models.CharField(
                choices=[
                    ('En attente', 'En attente'),
                    ('Planifié', 'Planifié'),
                    ('Validé', 'Validé'),
                    ('En cours', 'En cours'),
                    ('Retourné', 'Retourné'),
                    ('Expiré', 'Expiré'),
                    ('Annulé', 'Annulé'),
                ],
                default='En attente',
                max_length=90,
                verbose_name='État',
            ),
        ),
    ]
