# Generated by Django 3.1.5 on 2021-03-17 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0029_order_delivery_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
