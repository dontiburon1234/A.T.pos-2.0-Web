# Generated by Django 4.1 on 2023-08-28 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('atpos', '0012_alter_unidadmedida_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='codigoalterno',
            name='precio',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
