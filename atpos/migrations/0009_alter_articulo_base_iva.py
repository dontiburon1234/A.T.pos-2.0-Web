# Generated by Django 4.1 on 2023-08-24 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('atpos', '0008_alter_articulo_nombre_largo_articulo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo',
            name='base_iva',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='atpos.baseiva'),
        ),
    ]
