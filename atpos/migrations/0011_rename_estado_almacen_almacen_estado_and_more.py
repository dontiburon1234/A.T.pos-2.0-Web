# Generated by Django 4.1 on 2023-08-26 02:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atpos', '0010_alter_listaprecios_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='almacen',
            old_name='estado_almacen',
            new_name='estado',
        ),
        migrations.AddField(
            model_name='almacen',
            name='listaprecios',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='atpos.listaprecios'),
        ),
    ]
