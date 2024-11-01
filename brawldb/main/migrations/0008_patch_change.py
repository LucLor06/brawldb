# Generated by Django 5.0.6 on 2024-10-09 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_combo_options_legend_dexterity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=12)),
                ('link', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Change',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('working', 'Working'), ('outdated', 'Outdated'), ('average_damage', 'Average Damage'), ('dexterity', 'Dexterity'), ('start_damage', 'Start Damage'), ('stop_damage', 'Stop Damage')], max_length=64)),
                ('from_value', models.IntegerField(blank=True, null=True)),
                ('to_value', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='main.combo')),
                ('patch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='main.patch')),
            ],
        ),
    ]
