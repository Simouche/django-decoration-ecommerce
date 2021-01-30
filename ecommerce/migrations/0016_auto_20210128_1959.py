# Generated by Django 3.1.5 on 2021-01-28 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0015_auto_20210128_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveries',
            name='delivery_guys',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='ecommerce.deliveryguy', verbose_name='Delivery Guy'),
        ),
    ]
