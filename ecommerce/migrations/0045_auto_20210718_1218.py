# Generated by Django 3.1.5 on 2021-07-18 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0044_auto_20210712_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='raw_value',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Discount Value'),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount_percent',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Discount %'),
        ),
    ]
