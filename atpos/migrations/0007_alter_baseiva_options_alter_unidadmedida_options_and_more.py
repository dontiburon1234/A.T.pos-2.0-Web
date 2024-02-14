# Generated by Django 4.1 on 2023-08-23 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('atpos', '0006_cajaserie'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='baseiva',
            options={'default_permissions': (), 'permissions': [('add_baseiva', 'Base IVA crear'), ('change_baseiva', 'Base IVA modificar'), ('delete_baseiva', 'Base IVA eliminar'), ('view_baseiva', 'Base IVA ver')]},
        ),
        migrations.AlterModelOptions(
            name='unidadmedida',
            options={'default_permissions': (), 'permissions': [('add_unidadmedida', 'Unidad Medida crear'), ('change_unidadmedida', 'Unidad Medida modificar'), ('delete_unidadmedida', 'Unidad Medida eliminar'), ('view_unidadmedida', 'Unidad Medida ver')]},
        ),
        migrations.RenameField(
            model_name='articulo',
            old_name='estado_articulo',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='baseiva',
            old_name='estado_baseiva',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='codigoalterno',
            old_name='estado_codigoalterno',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='listaprecios',
            old_name='estado_listaprecios',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='listapreciosalmacen',
            old_name='estado_listaprecios_almacen',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='listapreciosarticulo',
            old_name='estado_listaprecios',
            new_name='estado',
        ),
        migrations.RenameField(
            model_name='unidadmedida',
            old_name='estado_categoria',
            new_name='estado',
        ),
        migrations.AlterUniqueTogether(
            name='baseiva',
            unique_together={('base_iva', 'nombre_base_iva')},
        ),
        migrations.AlterUniqueTogether(
            name='unidadmedida',
            unique_together={('codigo_unidad_medida', 'nombre_unidad_medida')},
        ),
    ]
