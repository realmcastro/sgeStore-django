# Generated by Django 5.1.4 on 2025-01-04 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockProducts', '0006_alter_products_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockhistory',
            name='action',
            field=models.CharField(choices=[('added', 'Produto Adicionado'), ('updated', 'Produto Atualizado'), ('deleted', 'Produto Deletado')], max_length=20),
        ),
    ]
