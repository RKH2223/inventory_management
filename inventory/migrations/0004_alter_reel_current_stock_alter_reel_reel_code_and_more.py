# Generated by Django 5.1.6 on 2025-02-14 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_alter_reel_size_mm"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reel",
            name="current_stock",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                editable=False,
                help_text="Current stock available in kg",
                max_digits=10,
            ),
        ),
        migrations.AlterField(
            model_name="reel",
            name="reel_code",
            field=models.CharField(
                help_text="Unique code for this reel", max_length=100, unique=True
            ),
        ),
        migrations.AlterField(
            model_name="reel",
            name="size_inch",
            field=models.DecimalField(
                decimal_places=2,
                help_text="Size in inch (e.g., 26.00 to 52.00)",
                max_digits=5,
            ),
        ),
    ]
