# Generated by Django 4.2.5 on 2023-09-10 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_statusemprestimo'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]