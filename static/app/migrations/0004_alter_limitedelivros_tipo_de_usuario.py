# Generated by Django 4.2.5 on 2023-09-10 00:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_tipodeemprestimo_limitedelivros'),
    ]

    operations = [
        migrations.AlterField(
            model_name='limitedelivros',
            name='tipo_de_usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.tipousuario'),
        ),
    ]
