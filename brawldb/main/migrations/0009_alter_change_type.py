# Generated by Django 5.0.6 on 2024-10-09 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_patch_change'),
    ]

    operations = [
        migrations.AlterField(
            model_name='change',
            name='type',
            field=models.CharField(max_length=64),
        ),
    ]
