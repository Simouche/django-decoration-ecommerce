# Generated by Django 3.1.2 on 2021-02-18 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0023_order_assigned_to'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='free_shipping',
            new_name='free_delivery',
        ),
    ]
