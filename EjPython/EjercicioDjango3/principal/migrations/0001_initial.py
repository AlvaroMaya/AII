# Generated by Django 4.1.6 on 2023-04-20 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DenominacionOrigen',
            fields=[
                ('idDenominacion', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.TextField(verbose_name='Denominacion')),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('idPais', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.TextField()),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Uva',
            fields=[
                ('idUva', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.TextField()),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.CreateModel(
            name='Vino',
            fields=[
                ('idVino', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.TextField(max_length=30, verbose_name='Nombre')),
                ('precio', models.FloatField(verbose_name='Precio')),
                ('denominacionOrigen', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='principal.denominacionorigen', verbose_name='Denominacion de origen')),
                ('tiposUvas', models.ManyToManyField(to='principal.uva')),
            ],
            options={
                'ordering': ('nombre',),
            },
        ),
        migrations.AddField(
            model_name='denominacionorigen',
            name='pais',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='principal.pais'),
        ),
    ]