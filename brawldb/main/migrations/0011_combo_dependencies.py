# Generated by Django 5.0.6 on 2024-10-09 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_combo_legend'),
    ]

    operations = [
        migrations.AddField(
            model_name='combo',
            name='dependencies',
            field=models.ManyToManyField(blank=True, related_name='dependent_combos', to='main.combo'),
        ),
    ]