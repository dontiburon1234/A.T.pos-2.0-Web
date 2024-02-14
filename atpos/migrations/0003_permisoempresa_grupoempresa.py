# Generated by Django 4.1 on 2023-07-25 23:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('atpos', '0002_usuario_tel_inicial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermisoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atpos.empresa')),
                ('permiso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.permission')),
            ],
            options={
                'unique_together': {('empresa', 'permiso')},
            },
        ),
        migrations.CreateModel(
            name='GrupoEmpresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='atpos.empresa')),
                ('grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
            ],
            options={
                'unique_together': {('empresa', 'grupo')},
            },
        ),
    ]
