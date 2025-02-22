# Generated by Django 5.1.6 on 2025-02-13 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_alter_reel_reel_code_alter_reel_size_inch'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reel',
            name='size_inch',
            field=models.DecimalField(decimal_places=2, help_text='Size in mm (e.g., 26.00 to 52.00)', max_digits=5),
        ),
    ]
