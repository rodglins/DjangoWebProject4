# Generated by Django 4.2.5 on 2023-09-13 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_tipodeemprestimo_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
            ],
        ),
    ]
