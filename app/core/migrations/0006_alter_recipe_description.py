# Generated by Django 3.2.16 on 2022-11-21 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20221121_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
