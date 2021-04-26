# Generated by Django 3.1.5 on 2021-04-24 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0031_remove_cartline_visible'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('standard_delivery_fee', models.PositiveIntegerField(default=500, help_text='Delivery feed for Alger, Boumerdes and Blida', verbose_name='Standard Delivery Fee')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='deliverycompany',
            name='default',
            field=models.BooleanField(default=False, verbose_name='Default'),
        ),
        migrations.AddField(
            model_name='product',
            name='weight',
            field=models.PositiveIntegerField(default=100, verbose_name='Weight'),
        ),
    ]