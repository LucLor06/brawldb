# Generated by Django 5.0.6 on 2024-10-16 15:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_combo_html_title_combo_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='change',
            name='combo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='main.combo'),
        ),
        migrations.AlterField(
            model_name='change',
            name='type',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]