# Generated by Django 4.1.3 on 2023-02-12 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_tax'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tax',
            options={'verbose_name_plural': 'tax'},
        ),
    ]