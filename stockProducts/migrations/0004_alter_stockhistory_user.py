# Generated by Django 5.1.4 on 2025-01-04 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockProducts', '0003_stockhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockhistory',
            name='user',
            field=models.CharField(max_length=50),
        ),
    ]
